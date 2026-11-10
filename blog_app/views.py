from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import BlogPost, BlogComment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from product_app.models import Category, Brand, Cart  # ✅ Cart رو اضافه کن


def blog_list(request):
    """لیست همه پست‌ها با صفحه‌بندی 2 تایی و قابلیت مرتب‌سازی"""

    # گرفتن پارامتر مرتب‌سازی
    sort_by = request.GET.get('sort', 'newest')

    posts_list = BlogPost.objects.filter(status='published')

    # مرتب‌سازی
    if sort_by == 'oldest':
        posts_list = posts_list.order_by('created_at')
    else:  # newest
        posts_list = posts_list.order_by('-created_at')

    # آخرین پست‌ها (برای سایدبار - اختیاری)
    recent_posts = BlogPost.objects.filter(status='published').order_by('-created_at')[:5]
    popular_posts = BlogPost.objects.filter(status='published').order_by('-views_count')[:5]

    # صفحه‌بندی: 2 پست در هر صفحه
    paginator = Paginator(posts_list, 2)
    page = request.GET.get('page', 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # ========== دسته‌بندی‌ها و برندها ==========
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    # =========================================

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

    context = {
        'posts': posts,
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
        'paginator': paginator,
        'page_obj': posts,
        'categories': categories,
        'brands': brands,
        'cart': cart,
        'cart_count': cart_count,
        'current_sort': sort_by,  # ✅ اضافه شد
    }
    return render(request, 'blog_app/blog-list.html', context)


def blog_detail(request, slug):
    """نمایش جزئیات پست"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # افزایش بازدید
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # نظرات تایید شده (نظرات اصلی، نه پاسخ‌ها)
    comments = post.comments.filter(is_approved=True, parent=None)

    # پست‌های مرتبط (بر اساس تاریخ)
    related_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(id=post.id).order_by('-created_at')[:3]

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
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    # ====================================================

    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'categories': categories,  # ✅ اضافه شد
        'brands': brands,  # ✅ اضافه شد
        'cart': cart,  # ✅ اضافه شد
        'cart_count': cart_count,  # ✅ اضافه شد
    }
    return render(request, 'blog_app/blog-details.html', context)


def blog_search(request):
    """جستجو در پست‌ها"""
    query = request.GET.get('q', '')
    if query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            status='published'
        )
    else:
        posts = BlogPost.objects.none()

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

    # ========== دسته‌بندی‌ها و برندها ==========
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    # ==========================================

    context = {
        'posts': posts,
        'query': query,
        'categories': categories,
        'brands': brands,
        'cart': cart,
        'cart_count': cart_count,
    }
    return render(request, 'blog_app/blog-search.html', context)
