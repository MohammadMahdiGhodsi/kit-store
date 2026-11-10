from django.urls import path
from . import views

app_name = 'accounts_otp'

urlpatterns = [
    path('register/', views.register_with_otp, name='register'),
    path('verify/', views.verify_otp, name='verify_otp'),  # حذف <int:user_id>
    path('resend/', views.resend_otp, name='resend_otp'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]
