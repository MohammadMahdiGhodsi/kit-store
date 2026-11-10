from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from accounts_otp.models import CustomUser
from product_app.models import Order, Cart
import jdatetime
from .models import UserAddress


def register_page(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not phone or not username or not password or not confirm_password:
            messages.error(request, 'تمامی فیلدهای ضروری باید پر شوند')
            return redirect('accounts_otp:register')

        if len(username) < 3:
            messages.error(request, 'نام کاربری باید حداقل 3 کاراکتر باشد')
            return redirect('accounts_otp:register')

        if len(username) > 30:
            messages.error(request, 'نام کاربری باید حداکثر 30 کاراکتر باشد')
            return redirect('accounts_otp:register')

        if not phone.isdigit() or len(phone) != 11:
            messages.error(request, 'لطفاً یک شماره تلفن 11 رقمی معتبر وارد کنید')
            return redirect('accounts_otp:register')

        if email:
            if '@' not in email or '.' not in email:
                messages.error(request, 'لطفاً یک ایمیل معتبر وارد کنید')
                return redirect('accounts_otp:register')
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'این ایمیل قبلاً ثبت شده است')
                return redirect('accounts_otp:register')

        if password != confirm_password:
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند')
            return redirect('accounts_otp:register')

        if len(password) < 6:
            messages.error(request, 'رمز عبور باید حداقل 6 کاراکتر باشد')
            return redirect('accounts_otp:register')

        simple_passwords = ['123456', 'password', '12345678', 'qwerty', 'abc123']
        if password in simple_passwords:
            messages.error(request, 'رمز عبور بسیار ساده است. لطفاً رمز قوی‌تری انتخاب کنید')
            return redirect('accounts_otp:register')

        if password.lower() == username.lower():
            messages.error(request, 'رمز عبور نباید با نام کاربری یکسان باشد')
            return redirect('accounts_otp:register')

        if not any(char.isdigit() for char in password):
            messages.warning(request, 'توصیه می‌شود رمز عبور شامل اعداد نیز باشد')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است')
            return redirect('accounts_otp:register')

        if CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره تلفن قبلاً ثبت شده است')
            return redirect('accounts_otp:register')

        user = CustomUser.objects.create_user(
            username=username,
            phone=phone,
            password=password
        )

        if email:
            user.email = email
            user.save()

        login(request, user)
        messages.success(request, f'👋 خوش آمدید {user.username} ! خوشحالیم که دوباره اومدی')
        return redirect('home-page')

    return render(request, 'accounts_otp/register.html')


def login_page(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if not phone or not password:
            messages.error(request, 'لطفاً شماره موبایل و رمز عبور را وارد کنید')
            return redirect('accounts_app:login')

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است')
            return redirect('accounts_app:login')

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'✨ خوش آمدید {user.username} !')
            return redirect('home-page')
        else:
            messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است')
            return redirect('accounts_app:login')

    return render(request, 'accounts_app/login.html')


def logout_page(request):
    logout(request)
    messages.success(request, '👋 شما با موفقیت خارج شدید')
    return redirect('home-page')


@login_required
def profile_page(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    addresses = UserAddress.objects.filter(user=request.user)

    # ========== سبد خرید ==========
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    # ================================

    jalali_date = jdatetime.date.fromgregorian(date=request.user.date_joined)
    jalali_joined_date = jalali_date.strftime("%Y/%m/%d")

    context = {
        'user': request.user,
        'orders': orders,
        'addresses': addresses,
        'jalali_joined_date': jalali_joined_date,
        'cart_count': cart_count,  # ✅ اضافه شد
    }
    return render(request, 'accounts_app/profile.html', context)


@login_required
def address_page(request):
    user_addresses = UserAddress.objects.filter(user=request.user)

    # ========== سبد خرید ==========
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    # ================================

    delete_id = request.GET.get('delete')
    if delete_id:
        try:
            addr = UserAddress.objects.get(id=delete_id, user=request.user)
            addr.delete()
            messages.success(request, '✅ آدرس با موفقیت حذف شد.')
        except:
            pass
        return redirect('accounts_app:address')

    default_id = request.GET.get('set_default')
    if default_id:
        UserAddress.objects.filter(user=request.user).update(is_default=False)
        UserAddress.objects.filter(id=default_id, user=request.user).update(is_default=True)
        messages.success(request, '✅ آدرس پیش‌فرض تغییر کرد.')
        return redirect('accounts_app:address')

    if request.method == 'POST':
        if len(user_addresses) >= 3:
            messages.error(request, '❌ حداکثر می‌توانید 3 آدرس ثبت کنید.')
            return redirect('accounts_app:address')

        receiver_name = request.POST.get('receiver_name', '')
        province = request.POST.get('province', '')
        city = request.POST.get('city', '')
        address = request.POST.get('address', '')
        postal_code = request.POST.get('postal_code', '')
        is_default = request.POST.get('is_default') == 'on'

        if not receiver_name or not province or not city or not address:
            messages.error(request, '❌ لطفاً تمام فیلدهای ضروری را پر کنید.')
            return redirect('accounts_app:address')

        if is_default:
            UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)

        UserAddress.objects.create(
            user=request.user,
            receiver_name=receiver_name,
            province=province,
            city=city,
            address=address,
            postal_code=postal_code,
            is_default=is_default
        )
        messages.success(request, '✅ آدرس جدید با موفقیت اضافه شد.')
        return redirect('accounts_app:address')

    context = {
        'addresses': user_addresses,
        'can_add': user_addresses.count() < 3,
        'max_addresses': 3,
        'cart_count': cart_count,  # ✅ اضافه شد
    }
    return render(request, 'accounts_app/address.html', context)


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # ========== سبد خرید ==========
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    # ================================

    for order in orders:
        order.jalali_date = jdatetime.date.fromgregorian(date=order.created_at).strftime("%Y/%m/%d")

    return render(request, 'accounts_app/orders.html', {
        'orders': orders,
        'cart_count': cart_count,  # ✅ اضافه شد
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    # ========== سبد خرید ==========
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    # ================================

    order.jalali_date = jdatetime.date.fromgregorian(date=order.created_at).strftime("%Y/%m/%d %H:%M")

    return render(request, 'accounts_app/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'cart_count': cart_count,  # ✅ اضافه شد
    })