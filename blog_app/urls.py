from django.urls import path
from . import views

app_name = 'blog_app'

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
]