from django.contrib import admin
from .models import Customer, Restaurant, MenuItem, Cart, CartItem, OrderItem

# Register your models here.

admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
