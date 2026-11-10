from django.db import models
from accounts_otp.models import CustomUser  # ایمپورت از accounts_otp

class UserAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    receiver_name = models.CharField(max_length=100, verbose_name="نام گیرنده")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    address = models.TextField(verbose_name="آدرس کامل")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    is_default = models.BooleanField(default=False, verbose_name="آدرس پیش‌فرض")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.receiver_name} - {self.province} - {self.city}"