import uuid
import razorpay
from django.conf import settings
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from adminpanel.models import Customer,Restaurant,MenuItem,Cart,CartItem,OrderItem

#Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.
def home(request):
    if request.user.is_superuser:
        return redirect('adminpanel:admin_dashboard')
    return render(request,'customer/base.html')


def login_view(request):

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('adminpanel:admin_dashboard')
        return redirect('customer:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password')
            return render(request, 'customer/login.html')

        # 🔑 Login user (both admin & customer allowed)
        login(request, user)

        if user.is_superuser:
            return redirect('adminpanel:admin_dashboard')
        else:
            return redirect('customer:home')

    return render(request, 'customer/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
           
        if User.objects.filter(username = username).exists():
            messages.error(request,'Username already exists,Try another one')
            return redirect('customer:register')
        
        if password1 != password2:
            messages.error(request,'Passwords do not match,Try again')
            return redirect('customer:register')
        
        user = User.objects.create_user(username=username,password=password1,email=email)
        
        #customer profile for the user
        Customer.objects.create(user=user)
       
        messages.success(request,'Registered successfully,You can now log in')
        
        return redirect('customer:login')
    
    return render(request,'customer/register.html')

@login_required(login_url='customer:login')
def logout_view(request):
    logout(request)
    messages.success(request,'Logged out successfully')
    return redirect('customer:home')

@login_required(login_url='customer:login')
def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request,'customer/restaurant_list.html',{'restaurants':restaurants})


@login_required(login_url='customer:login')
def menu_list(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant,id=restaurant_id)
    
    menu_items = restaurant.menuitem_set.all()
    return render(request,'customer/menu_list.html',{'restaurant':restaurant,
                                                       'menu_items':menu_items})


def menu_details(request,item_id):
    menu_items = get_object_or_404(MenuItem, id=item_id)
    return render(request,'customer/menu_detail.html',{'menu_items':menu_items})

@login_required(login_url='customer:login')
def add_to_cart(request,item_id):
    action = request.GET.get('action','add')
    food_item = get_object_or_404(MenuItem,id=item_id)
    
    #check login
    if not request.user.is_authenticated:
        return redirect('customer:login')
    
    #get or create customer
    customer, _ = Customer.objects.get_or_create(user = request.user)
    #get or create cart for customer
    cart,created = Cart.objects.get_or_create(customer = customer)
    
     # 🔴 Restaurant closed check
    if not food_item.restaurant.is_open:
        messages.error(request, "This restaurant is currently closed.")
        return redirect('customer:restaurants')
    #add or update cart item
    cart_item,created = CartItem.objects.get_or_create(
        cart=cart,
        food_item=food_item
    )
    # Add quantity 
    if action == "add" and not created:
        cart_item.quantity += 1
        cart_item.save()

    # Decrease quantity(minimum 1)
    elif action == "remove":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        
    return redirect('customer:cart_page')

@login_required(login_url='customer:login')
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    #  only allow the owner to delete
    if cart_item.cart.customer.user == request.user:
        cart_item.delete()

    return redirect('customer:cart_page')


@login_required(login_url='customer:login')
def cart_page(request):
    customer,_ = Customer.objects.get_or_create(user=request.user)
    cart,_ = Cart.objects.get_or_create(customer=customer)
    
    items = CartItem.objects.filter(cart=cart)
    total = cart.get_total()
    
    context = {
        'cart': cart,
        'items': items,
        'total': total,
    }

    return render(request, 'customer/cart.html', context)


@login_required(login_url='customer:login')
def order_single_item(request,cart_item_id):
    
    customer = get_object_or_404(Customer,user= request.user)
    
    cart_item = get_object_or_404(CartItem,
                                  id=cart_item_id,
                                  cart__customer=customer)
    
    checkout_id = uuid.uuid4()
    
    OrderItem.objects.create(
        customer=customer,
        restaurant=cart_item.food_item.restaurant,
        food_item=cart_item.food_item,
        quantity=cart_item.quantity,
        checkout_id=checkout_id
    )
    
    
    return redirect('customer:payment',checkout_id=checkout_id)
   
@login_required(login_url='customer:login')
def order_all_item(request):
    
    customer = get_object_or_404(Customer,user=request.user)
    cart_items = CartItem.objects.filter(cart__customer=customer)
    
    if not cart_items.exists():
        messages.error(request,'Your cart is empty')
        return redirect('customer:cart_page')
    
    checkout_id = uuid.uuid4()
    
    for cart_item in cart_items:
        OrderItem.objects.create(
            customer=customer,
            restaurant=cart_item.food_item.restaurant,
            food_item=cart_item.food_item,
            quantity=cart_item.quantity,
            checkout_id=checkout_id
        )
    
    
    return redirect('customer:payment',checkout_id=checkout_id)


@login_required(login_url='customer:login')
def payment_page(request, checkout_id=None):
    customer = get_object_or_404(Customer, user=request.user)

    order_items = OrderItem.objects.filter(
        customer=customer,
        checkout_id=checkout_id,
        is_paid=False
    )

    if not order_items.exists():
        return HttpResponse("No pending orders to pay.")

    # Calculate total in INR
    total_amount_inr = sum(item.food_item.price * item.quantity for item in order_items)

    # Convert to paisa for Razorpay
    total_amount = int(total_amount_inr * 100)

    razorpay_order = client.order.create({
        "amount": total_amount,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "order_items": order_items,
        "total_amount": total_amount,           # paisa
        "total_amount_inr": total_amount_inr,   # rupees
        "checkout_id": checkout_id,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    }

    return render(request, "customer/payment_page.html", context)

@csrf_exempt
@login_required(login_url='customer:login')
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        checkout_id = request.POST.get('checkout_id')
        
        customer = get_object_or_404(Customer,user=request.user)
        order_items = OrderItem.objects.filter(customer=customer,
                                              checkout_id=checkout_id,
                                              is_paid=False)
        
        for item in order_items:
            item.is_paid = True
            item.save()
            
        # clear cart
        CartItem.objects.filter(cart__customer=customer).delete()
        
        return render(request, "customer/payment_success.html")
    return HttpResponse("Invalid request method.")