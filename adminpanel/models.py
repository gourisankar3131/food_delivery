from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=15,blank=True, null=True)
    address = models.TextField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.user.username 
    
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15) 
    is_open = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
       return f"{self.name} - {self.location}"
   
class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class Cart(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    
    #  cart total calculation
    def get_total(self):
        return sum(item.get_subtotal() for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart of {self.customer.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    food_item = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
     
    #subtotal 
    def get_subtotal(self):
        return self.quantity * self.food_item.price
    
    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('out_for_delivery','Out_for_delivery'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    ]
    
    checkout_id = models.UUIDField(null=True, blank=True)
    
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    food_item = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    is_paid = models.BooleanField(default=False)
    

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username} ({self.status})"
    
class Payment(models.Model):
    order = models.OneToOneField(OrderItem,on_delete=models.CASCADE,related_name='payment')
    method = models.CharField(max_length=20,choices=[('cod','Cash on delivery'),('upi','UPI')])
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)    
    
    def __str__(self):
        return f"Payment for Order {self.order.id}"