
from django.urls import path
from adminpanel import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard',views.admin_dashboard, name='admin_dashboard'),
    path('login/',views.admin_login,name='admin_login'),
    path('admin_register/',views.register,name='register'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('add_restaurant/',views.add_restaurant,name='add_restaurant'),
    path('restaurant_list/',views.restaurant_list,name='restaurant_list'),
    path('update_restaurant/<int:restaurant_id>/',views.update_restaurant,name='update_restaurant'),
    path('add_menu/<int:restaurant_id>/',views.add_menu,name='add_menu'),
    path('menu_list/<int:restaurant_id>/',views.menu_list,name='menu_list'),
    path('update_menu/<int:menu_item_id>/',views.update_menu,name='update_menu'),
    path('menu_list/', views.menu_list_all, name='menu_list_all'),
    path('delete_menu/<int:menu_item_id>/',views.delete_menu,name='delete_menu'),
    ]
