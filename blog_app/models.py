from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
# from django.contrib.auth.models import User
from datetime import datetime


class BlogPost(models.Model):
    """مدل پست بلاگ"""
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="آدرس پست", allow_unicode=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="نویسنده")

    # خلاصه و محتوا
    excerpt = models.TextField(verbose_name="خلاصه مطلب", max_length=500,
                               help_text="مختصری از مطلب (حداکثر 500 کاراکتر)", blank=True, null=True)
    content = models.TextField(verbose_name="محتوای کامل")

    # تصاویر
    featured_image = models.ImageField(upload_to="blog/images/", verbose_name="تصویر شاخص", null=True, blank=True)

    # متادیتا
    views_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت")

    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انتشار")

    class Meta:
        verbose_name = "پست بلاگ"
        verbose_name_plural = "پست‌های بلاگ"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = datetime.now()
        super().save(*args, **kwargs)


class BlogComment(models.Model):
    """نظرات پست‌ها"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name="پست")
    name = models.CharField(max_length=100, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    comment = models.TextField(verbose_name="نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                               verbose_name="پاسخ به")  # ← این خط اضافه شد

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.post.title}"
