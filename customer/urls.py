from django.urls import path
from customer import views

app_name = 'customer'

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',views.login_view, name='login'),
    path("register/", views.register, name="register"),
    path('logout/',views.logout_view, name='logout'),
    path('restaurants/',views.restaurant_list, name='restaurants'),
    path('menu/<int:restaurant_id>/',views.menu_list,name='menu_list'),
    
    
# Cart item management URLs
    path('cart/',views.cart_page,name='cart_page'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
   

    # order URLs
    path('order_single_item/<int:cart_item_id>/', views.order_single_item, name='order_single_item'),
    path('order_cart_items/', views.order_all_item, name='order_all_items'),

    # payment URLs
    path('payment/<uuid:checkout_id>/', views.payment_page, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]
