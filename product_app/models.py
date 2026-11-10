from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """مدل دسته‌بندی محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس دسته‌بندی", allow_unicode=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    image = models.ImageField(upload_to="categories/", verbose_name="تصویر دسته‌بندی", null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subs',
                               verbose_name="دسته‌بندی والد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_products', args=[self.slug])


class Brand(models.Model):
    """مدل برند محصولات"""
    name = models.CharField(max_length=100, verbose_name="نام برند")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس برند", allow_unicode=True)
    logo = models.ImageField(upload_to="brands/logos/", verbose_name="لوگو", null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('brand_products', args=[self.slug])


class ProductModel(models.Model):
    """مدل برای صفحه جزئیات محصول"""

    # ارتباط با دسته‌بندی و برند
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                                 verbose_name="دسته‌بندی")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                              verbose_name="برند")

    # اطلاعات اصلی
    title = models.CharField(max_length=100, verbose_name="عنوان محصول")
    short_description = models.TextField(verbose_name="توضیح کوتاه", null=True, blank=True)
    long_description = models.TextField(verbose_name="توضیحات کامل")
    price = models.IntegerField(verbose_name="قیمت (تومان)")
    specifications = models.TextField(verbose_name="مشخصات محصول", null=True, blank=True,
                                      help_text="مشخصات فنی محصول را وارد کنید")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")

    # تصویر اصلی
    # main_image = models.ImageField(upload_to="products/main/", verbose_name="تصویر اصلی")
    def get_main_image(self):
        """بازگرداندن اولین تصویر گالری یا تصویر پیش‌فرض"""
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return '/static/images/default.jpg'

    def has_images(self):
        return self.images.exists()

    # گزینه‌ها
    colors = models.CharField(
        max_length=200,
        verbose_name="رنگ‌ها (با کاما جدا کنید)",
        help_text="مثال: قرمز,آبی,سبز,مشکی,سفید (بدون فاصله بعد از کاما)",
        null=True,
        blank=True
    )

    sizes = models.CharField(
        max_length=100,
        verbose_name="سایزها (با کاما جدا کنید)",
        help_text="مثال: S,M,L,XL (بدون فاصله بعد از کاما)",
        null=True,
        blank=True
    )

    # وضعیت
    in_stock = models.BooleanField(default=True, verbose_name="موجود")
    quantity = models.IntegerField(default=1, verbose_name="تعداد موجودی")

    # متادیتا
    views_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "جزئیات محصول"
        verbose_name_plural = "جزئیات محصولات"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # حذف فاصله‌های اضافی از رنگ‌ها و سایزها
        if self.colors:
            # حذف فاصله‌های اضافی بین آیتم‌ها
            colors_list = [color.strip() for color in self.colors.split(',')]
            self.colors = ','.join(colors_list)

        if self.sizes:
            # حذف فاصله‌های اضافی بین آیتم‌ها
            sizes_list = [size.strip() for size in self.sizes.split(',')]
            self.sizes = ','.join(sizes_list)

        super().save(*args, **kwargs)


class ProductComment(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='comments')
    user_name = models.CharField(max_length=100, verbose_name='نام کاربری')
    user_email = models.EmailField(verbose_name='ایمیل', blank=True, null=True)
    text = models.TextField(verbose_name='متن دیدگاه')
    rating = models.PositiveSmallIntegerField(verbose_name='امتیاز', choices=[(i, i) for i in range(1, 6)], null=True,
                                              blank=True)
    is_active = models.BooleanField(default=False, verbose_name='تایید شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'دیدگاه'
        verbose_name_plural = 'دیدگاه‌ها'

    def __str__(self):
        return f'{self.user_name} - {self.product.title[:30]}'

    def is_reply(self):
        return self.parent is not None


# ========== مدل‌های سبد خرید (خارج از ProductComment) ==========
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"سبد خرید {self.user.phone}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    class Meta:
        unique_together = ('cart', 'product', 'color', 'size')


class Order(models.Model):
    SHIPPING_METHODS = (
        ('express', 'پست پیشتاز'),
        ('tipax', 'تیپاکس'),
    )

    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.IntegerField()

    # اطلاعات ارسال
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHODS, default='express')
    shipping_cost = models.IntegerField(default=0)

    def __str__(self):
        return f"سفارش #{self.id} - {self.user.phone}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()  # قیمت زمان خرید
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class ProductImage(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='تصویر')
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='متن جایگزین')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'گالری تصاویر'

    def __str__(self):
        return f"{self.product.title} - تصویر {self.order}"
