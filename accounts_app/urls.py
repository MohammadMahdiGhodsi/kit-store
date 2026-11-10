from django.urls import path
from . import views

app_name = 'accounts_app'

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.profile_page, name='profile'),
    path('address/', views.address_page, name='address'),
    path('orders/', views.orders_list, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail')
]
