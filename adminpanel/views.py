from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Restaurant,MenuItem,OrderItem
from adminpanel.forms import RestaurantForm,MenuItemForm

# Create your views here.

def admin_dashboard(request):
    # 🔐 Protect admin dashboard
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminpanel:admin_login')

    restaurants = Restaurant.objects.all()
    restaurant_count = Restaurant.objects.count()
    menu_count = MenuItem.objects.count()

    context = {
        'restaurants': restaurants,
        'restaurant_count': restaurant_count,
        'menu_count': menu_count,
    }

    return render(request, 'adminpanel/dashboard.html', context)


def admin_login(request):
    # If already logged in as admin, go to dashboard
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('adminpanel:admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        # if user is not None and user.is_superuser:
        #     login(request, user)
        #     messages.success(request, "Admin logged in successfully")
        #     return redirect('adminpanel:admin_dashboard')
        # else:
            # messages.error(request, "Invalid admin credentials")

    return render(request, 'adminpanel/admin_login.html')
def admin_logout(request):
    logout(request)
    return redirect('adminpanel:admin_login')

def register(request):
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already taken")
        
        else:
        #create superuser
            user = User.objects.create_superuser(username=username,password=password)
            messages.success(request,"Admin registered successfully")
        return redirect('adminpanel:admin_login')
        
    return render(request,'adminpanel/register.html')

def admin_logout(request):
    logout(request)
    return redirect('adminpanel:admin_login')

def add_restaurant(request):
    form = RestaurantForm()
    if request.method == 'POST':
        form = RestaurantForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Restaurant added successfully")
            return redirect('adminpanel:restaurant_list')
        else:
            messages.error(request, "There was an error adding the restaurant. Please try again.")
    else:
            form = RestaurantForm()
    return render(request,'adminpanel/add_restaurant.html',{'form':form})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request,'adminpanel/restaurant_list.html',{'restaurants':restaurants})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully')
            return redirect('adminpanel:restaurant_list')
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'adminpanel/update_restaurant.html', {'form': form,'restaurant':restaurant})

    
def add_menu(request, restaurant_id):
    form = MenuItemForm()
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request,"Menu item added successfully")
            return redirect('adminpanel:menu_list', restaurant_id=restaurant_id)
           
    
    return render(request,'adminpanel/add_menu.html',{'form':form,
                                                      'restaurant':restaurant}) 
 
              
def menu_list(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant,id=restaurant_id)
    menu_items = restaurant.menuitem_set.all()
    return render(request,'adminpanel/menu_list.html',{'restaurant':restaurant,
                                                       'menu_items':menu_items})

def menu_list_all(request):
    menu_items = MenuItem.objects.select_related('restaurant')
    return render(request, 'adminpanel/menu_list_all.html', {'menu_items': menu_items})

def update_menu(request,menu_item_id):
    menu_item = get_object_or_404(MenuItem,id=menu_item_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST,request.FILES,instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request,"Menu item updated successfully")
            return redirect('adminpanel:menu_list',restaurant_id=menu_item.restaurant.id)
    else:
        form=MenuItemForm(instance=menu_item)
        return render(request,'adminpanel/update_menu.html',{'form':form,
                                                             'menu_item':menu_item})
    
def delete_menu(request,menu_item_id):
    menu_item = get_object_or_404(MenuItem, id= menu_item_id)
    menu_item.delete()
    messages.success(request,'Item deleted successfully')
    return redirect('adminpanel:menu_list_all')
    
# def payment_orders(request):
#     orders = OrderItem.objects