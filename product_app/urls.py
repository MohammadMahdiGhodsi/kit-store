from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('list/', views.product_list, name='product_list'),
    path('detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('brand/<slug:slug>/', views.brand_products, name='brand_products'),  # این خط رو اضافه کن
    path('kits/', views.kit_products, name='kit_products'),
    path('kit-meli/', views.kit_meli_products, name='kit-meli'),
    path('kit-club/', views.kit_club_products, name='kit-club'),
    path('shoes/', views.shoes_products, name='shoes'),
    path('shoes/', views.shoes_products, name='shoes_products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
]
