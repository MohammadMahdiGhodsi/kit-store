from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    phone = models.CharField(max_length=11, unique=True, verbose_name="شماره تلفن")
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name="استان")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="شهر")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="کد پستی")
    receiver_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام گیرنده")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return f"{self.username} - {self.phone}"


# accounts_otp/models.py
class OTPCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, verbose_name="کد تایید")
    phone = models.CharField(max_length=11, verbose_name='شماره تلفن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    expires_at = models.DateTimeField(verbose_name="زمان انقضا", null=True, blank=True)  # برگردون به حالت قبل
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")

    class Meta:
        verbose_name = "کد OTP"
        verbose_name_plural = "کدهای OTP"
        ordering = ['-created_at']

    def __str__(self):
        return f"کد {self.code} برای {self.phone}"

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    def create_otp(cls, user, phone):
        cls.objects.filter(user=user, is_used=False, expires_at__lt=timezone.now()).delete()
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=5)
        otp = cls.objects.create(
            user=user,
            phone=phone,
            code=code,
            expires_at=expires_at
        )
        return otp
