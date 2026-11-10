from django.shortcuts import render
from product_app.models import ProductModel, Category, Brand, Cart
from blog_app.models import BlogPost
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def home_page(request):

    # گرفتن عبارت جستجو از URL
    search_query = request.GET.get('search', '')

    # محصولات بر اساس جستجو
    if search_query:
        all_products = ProductModel.objects.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(long_description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        ).order_by('-created_at')
        search_result_count = all_products.count()
    else:
        all_products = ProductModel.objects.all().order_by('-created_at')
        search_result_count = 0

    # جدیدترین محصولات
    new_products = ProductModel.objects.all().order_by('-created_at')[:8]

    # محصولات کفش
    shoes_category = Category.objects.filter(slug='shoes').first()
    if shoes_category:
        shoes_products = ProductModel.objects.filter(category=shoes_category).order_by('-created_at')[:8]
    else:
        shoes_products = ProductModel.objects.none()

    # محصولات کیت‌ها
    kit_categories = Category.objects.filter(slug__startswith='kit')
    kit_products = ProductModel.objects.filter(category__in=kit_categories).order_by('-created_at')[:8]

    # بقیه موارد
    categories = Category.objects.all()
    brands = Brand.objects.all()
    latest_posts = BlogPost.objects.filter(status='published').order_by('-created_at')[:4]

    # ========== سبد خرید ==========
    cart = None
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
            print(f"✅ کاربر: {request.user.username} - تعداد سبد خرید: {cart_count}")
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
            cart_count = 0
            print(f"✅ سبد خرید جدید برای کاربر {request.user.username} ساخته شد")
    else:
        print("⚠️ کاربر لاگین نیست")
    # ================================

    return render(request, 'home-page.html', {
        'all_products': all_products,
        'new_products': new_products,
        'kit_products': kit_products,
        'categories': categories,
        'shoes_products': shoes_products,
        'brands': brands,
        'latest_posts': latest_posts,
        'search_query': search_query,
        'search_result_count': search_result_count,
        'cart': cart,
        'cart_count': cart_count,
    })


from django.shortcuts import render
from product_app.models import Category, Brand, Cart


def about_us(request):
    """صفحه درباره ما"""

    # ========== سبد خرید ==========
    cart = None
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
            cart_count = 0
    # ================================

    # ========== دسته‌بندی‌ها و برندها برای منو ==========
    categories = Category.objects.all()
    brands = Brand.objects.all()
    # ====================================================

    return render(request, 'about-us.html', {
        'cart': cart,
        'cart_count': cart_count,
        'categories': categories,
        'brands': brands,
    })


def contact_us(request):
    """صفحه تماس با ما"""

    # ========== سبد خرید ==========
    cart = None
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=request.user)
            cart_count = 0
    # ================================

    # ========== دسته‌بندی‌ها و برندها برای منو ==========
    categories = Category.objects.all()
    brands = Brand.objects.all()
    # ====================================================

    return render(request, 'contact-us.html', {
        'cart': cart,
        'cart_count': cart_count,
        'categories': categories,
        'brands': brands,
    })
