from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts_app.models import UserAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import (
    ProductModel, Category, Brand, ProductComment,
    Cart, CartItem, Order, OrderItem
)
from .forms import CommentForm
from product_app.models import Order, Cart, Category  # Category رو اضافه کن


def product_list(request):
    # گرفتن عبارت جستجو
    search_query = request.GET.get('search', '')

    # همه محصولات
    products = ProductModel.objects.all()

    # اگه جستجو انجام شده، فیلتر کن
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )

    # مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    else:
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # دسته‌بندی‌ها
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    # ========== اضافه کردن سبد خرید کاربر جاری ==========
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_sort': sort_by,
        'search_query': search_query,
        'cart': cart,  # ← این خط رو اضافه کن
    })


def product_detail(request, product_id):
    product = get_object_or_404(ProductModel, id=product_id)
    comments = ProductComment.objects.filter(product=product, is_active=True, parent=None)
    product_images = product.images.all()

    # اضافه کردن سبد خرید کاربر جاری
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.POST.get('submit_comment'):
        # فقط کاربران لاگین شده
        if not request.user.is_authenticated:
            messages.error(request, '❌ برای ثبت دیدگاه باید وارد حساب کاربری خود شوید.')
            return redirect('product_detail', product_id=product.id)

        # بررسی محدودیت 5 دقیقه
        last_comment = ProductComment.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()

        if last_comment:
            time_passed = (timezone.now() - last_comment.created_at).seconds // 60
            remaining = 5 - time_passed

            if remaining > 0:
                messages.error(request,
                               f'⏱️ شما فقط هر 5 دقیقه می‌توانید یک دیدگاه ثبت کنید. لطفاً {remaining} دقیقه دیگر تلاش کنید.')
                return redirect('product_detail', product_id=product.id)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.user_name = request.POST.get('user_name')
            comment.user_email = request.POST.get('user_email')
            comment.rating = request.POST.get('rating')
            comment.save()
            messages.success(request, '✅ دیدگاه شما با موفقیت ثبت شد. پس از تایید نمایش داده می‌شود.')
            return redirect('product_detail', product_id=product.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = CommentForm()

    suggested_products = ProductModel.objects.exclude(id=product_id)[:4]
    categories = Category.objects.filter(is_active=True, parent__isnull=True)

    return render(request, 'product-detail.html', {
        'product': product,
        'suggested_products': suggested_products,
        'categories': categories,
        'comments': comments,
        'comment_form': form,
        'product_images': product_images,
        'cart': cart,  # ← این خط مهمه
    })


def category_products(request, slug):
    """نمایش محصولات یک دسته‌بندی خاص با قابلیت مرتب‌سازی"""
    from django.core.paginator import Paginator
    from .models import Category, ProductModel, Brand

    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = ProductModel.objects.filter(category=category)

    # گرفتن پارامتر مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')

    # مرتب‌سازی
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count', '-created_at')
    else:  # newest
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # گرفتن همه دسته‌بندی‌ها و برندها برای منو
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'category': category,
        'categories': categories,  # ← اضافه شد
        'brands': brands,  # ← اضافه شد
        'page_title': category.name,
        'current_sort': sort_by,
        'cart': cart,
    })


def brand_products(request, slug):
    """نمایش محصولات یک برند خاص"""
    from django.core.paginator import Paginator
    from .models import Brand, ProductModel, Category

    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = ProductModel.objects.filter(brand=brand, in_stock=True)

    # مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    else:
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # گرفتن همه دسته‌بندی‌ها و برندها برای منو
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'brand': brand,
        'categories': categories,  # ← اضافه شد
        'brands': brands,  # ← اضافه شد
        'page_title': f'محصولات {brand.name}',
        'current_sort': sort_by,
        'cart': cart,
    })


def kit_products(request):
    """نمایش همه محصولات کیت‌های ورزشی (دسته‌بندی با slug شروع شونده با kit)"""
    # پیدا کردن همه دسته‌بندی‌هایی که با kit شروع میشن
    kit_categories = Category.objects.filter(slug__startswith='kit')

    # محصولات این دسته‌بندی‌ها
    products = ProductModel.objects.filter(category__in=kit_categories)

    # گرفتن پارامتر مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')

    # مرتب‌سازی
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count', '-created_at')
    else:  # newest
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'page_title': 'کیت‌های ورزشی',
        'current_sort': sort_by,
        'cart': cart,
    })


def kit_meli_products(request):
    """نمایش کیت‌های ملی"""
    kit_meli_category = Category.objects.filter(slug='kit-meli').first()

    if kit_meli_category:
        products = ProductModel.objects.filter(category=kit_meli_category, in_stock=True)
    else:
        products = ProductModel.objects.none()

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'page_title': 'کیت‌های ملی',
        'current_sort': request.GET.get('sort', 'newest'),
        'cart': cart,
    })


def kit_club_products(request):
    """نمایش کیت‌های باشگاهی"""
    kit_club_category = Category.objects.filter(slug='kit-club').first()

    if kit_club_category:
        products = ProductModel.objects.filter(category=kit_club_category, in_stock=True)
    else:
        products = ProductModel.objects.none()

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'page_title': 'کیت‌های باشگاهی',
        'current_sort': request.GET.get('sort', 'newest'),
        'cart': cart,
    })


def shoes_products(request):
    """نمایش همه محصولات دسته کفش (با slug='shoes')"""
    # پیدا کردن دسته‌بندی کفش
    shoes_category = Category.objects.filter(slug='shoes', is_active=True).first()

    if shoes_category:
        products = ProductModel.objects.filter(category=shoes_category, in_stock=True)
    else:
        products = ProductModel.objects.none()

    # گرفتن پارامتر مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')

    # مرتب‌سازی
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count', '-created_at')
    else:  # newest
        products = products.order_by('-created_at')

    # صفحه‌بندی
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    return render(request, 'product-list.html', {
        'page_obj': page_obj,
        'page_title': 'کفش‌های ورزشی',
        'current_sort': sort_by,
        'cart': cart,
    })


@login_required
def add_to_cart(request, product_id):
    # پیدا کردن محصول
    product = get_object_or_404(ProductModel, id=product_id)

    # پیدا کردن یا ایجاد سبد خرید برای کاربر
    cart, created = Cart.objects.get_or_create(user=request.user)

    # گرفتن اطلاعات از فرم
    color = request.POST.get('color', '').strip()
    size = request.POST.get('size', '').strip()
    quantity = int(request.POST.get('quantity', 1))

    # اگر رنگ یا سایز انتخاب نشده بود
    if not color or not size:
        messages.error(request, '❌ لطفاً رنگ و سایز را انتخاب کنید')
        return redirect('product_detail', product_id=product.id)

    # بررسی موجودی
    if quantity > product.stock:
        messages.error(request, f'❌ موجودی کافی نیست! فقط {product.stock} عدد از این محصول موجود است.')
        return redirect('product_detail', product_id=product.id)

    # حذف آیتم‌های تکراری قبلی (اگر وجود داشته باشند)
    CartItem.objects.filter(
        cart=cart,
        product=product,
        color=color,
        size=size
    ).delete()

    # ایجاد آیتم جدید در سبد خرید
    CartItem.objects.create(
        cart=cart,
        product=product,
        color=color,
        size=size,
        quantity=quantity
    )

    # پیام موفقیت
    messages.success(request, f'✅ {product.title} (رنگ {color} - سایز {size}) با موفقیت به سبد خرید اضافه شد.')

    # رفتن به صفحه سبد خرید
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    # گرفتن تمام دسته‌بندی‌های اصلی (که parent ندارن)
    categories = Category.objects.filter(parent__isnull=True, is_active=True)

    context = {
        'cart': cart,
        'categories': categories,
    }
    return render(request, 'product_app/cart-detail.html', context)


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    # بررسی موجودی
    if quantity > cart_item.product.stock:
        messages.error(request, f'❌ موجودی کافی نیست! فقط {cart_item.product.stock} عدد از این محصول موجود است.')
        return redirect('cart_detail')

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'✅ تعداد محصول "{cart_item.product.title}" به {quantity} تغییر یافت.')
    else:
        cart_item.delete()
        messages.success(request, f'❌ محصول "{cart_item.product.title}" از سبد خرید حذف شد.')

    return redirect('cart_detail')


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    messages.success(request, f'❌ محصول "{product_title}" از سبد خرید حذف شد.')
    return redirect('cart_detail')


@login_required
def clear_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    messages.success(request, '✅ همه محصولات از سبد خرید حذف شدند.')
    return redirect('cart_detail')


from django.contrib import messages

from product_app.models import Order, Cart, Category, Brand  # Category و Brand رو اضافه کن


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    # اگر سبد خرید خالی است
    if not cart.items.exists():
        messages.error(request, '❌ سبد خرید شما خالی است!')
        return redirect('cart_detail')

    # دریافت سفارش‌های قبلی کاربر
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # دریافت آدرس‌های ذخیره شده کاربر
    user_addresses = UserAddress.objects.filter(user=request.user)

    # ✅ دریافت دسته‌بندی‌ها برای منوی همبرگر
    categories = Category.objects.all()  # اگر فیلد is_active داری، از filter استفاده کن
    brands = Brand.objects.all()  # برای برندها

    if request.method == 'POST':
        # گرفتن استان و شهر
        province = request.POST.get('province', '')
        city = request.POST.get('city', '')

        # گرفتن روش ارسال
        shipping_method = request.POST.get('shipping_method', 'express')
        shipping_cost = int(request.POST.get('shipping_cost', 0))

        # محاسبه قیمت کل
        total_price = cart.get_total_price() + shipping_cost

        # ایجاد سفارش جدید از سبد خرید
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            province=province,
            city=city,
            address=request.POST.get('address', ''),
            phone=request.POST.get('phone', ''),
            postal_code=request.POST.get('postal_code', ''),
            notes=request.POST.get('notes', ''),
            shipping_method=shipping_method,
            shipping_cost=shipping_cost,
            status='pending'
        )

        # ایجاد آیتم‌های سفارش
        from product_app.models import OrderItem
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                color=item.color,
                size=item.size
            )

        # خالی کردن سبد خرید
        cart.items.all().delete()

        # ذخیره آدرس در پروفایل کاربر
        user = request.user
        user.province = province
        user.city = city
        user.address = request.POST.get('address', '')
        user.postal_code = request.POST.get('postal_code', '')
        user.receiver_name = f"{request.POST.get('first_name', '')} {request.POST.get('last_name', '')}"
        user.save()

        messages.success(request, f'✅ سفارش شما با موفقیت ثبت شد!|شماره سفارش: #{order.id}')
        return redirect('home-page')

    return render(request, 'product_app/checkout.html', {
        'cart': cart,
        'orders': orders,
        'user_addresses': user_addresses,
        'categories': categories,  # ✅ اضافه شد
        'brands': brands,  # ✅ اضافه شد (اختیاری)
    })
