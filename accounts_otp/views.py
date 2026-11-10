from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import OTPCode
from accounts_otp.models import CustomUser
from datetime import timedelta
import random
import requests
from django.contrib.auth import get_user_model

User = get_user_model()

import random
import requests
from django.conf import settings


def generate_otp_code():
    """تولید کد تایید 6 رقمی"""
    return ''.join(random.choices('0123456789', k=6))


def send_otp_sms(phone_number, code):
    """ارسال کد تایید با الگوی آماده"""
    body_id = 524  # ← عدد واقعی رو از پنل بگیر

    data = {
        'bodyId':456934,
        'to': phone_number,
        'args': [code]
    }

    api_key = 'ad790de2df3a47f5982a68e55d03a901'
    url = f'https://console.melipayamak.com/api/send/shared/{api_key}'

    print(f"📱 ارسال به: {phone_number}")
    print(f"🔑 کد: {code}")

    try:
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        print(f"✅ پاسخ: {result}")

        # بررسی موفقیت آمیز بودن ارسال
        if response.status_code == 200 and 'recId' in result:
            print("✅ پیامک با موفقیت ارسال شد")
            return True
        else:
            print("❌ خطا در ارسال پیامک")
            return False

    except Exception as e:
        print(f"❌ خطا: {e}")
        return False


def register_with_otp(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # اعتبارسنجی
        if not phone or not username or not password or not confirm_password:
            messages.error(request, 'تمامی فیلدها باید پر شوند')
            return redirect('accounts_otp:register')

        if len(username) < 3:
            messages.error(request, 'نام کاربری باید حداقل 3 کاراکتر باشد')
            return redirect('accounts_otp:register')

        if not phone.isdigit() or len(phone) != 11:
            messages.error(request, 'شماره تلفن باید 11 رقم باشد')
            return redirect('accounts_otp:register')

        if password != confirm_password:
            messages.error(request, 'رمز عبور مطابقت ندارد')
            return redirect('accounts_otp:register')

        if len(password) < 6:
            messages.error(request, 'رمز عبور باید حداقل 6 کاراکتر باشد')
            return redirect('accounts_otp:register')

        # بررسی کاربر تکراری
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است')
            return redirect('accounts_otp:register')

        if CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره تلفن قبلاً ثبت شده است')
            return redirect('accounts_otp:register')

        # ساخت کاربر غیرفعال
        user = CustomUser.objects.create_user(
            username=username,
            phone=phone,
            password=password,
            is_active=False
        )

        # تولید کد OTP
        otp_code = generate_otp_code()

        # ذخیره در دیتابیس
        OTPCode.objects.create(
            user=user,
            code=otp_code,
            phone=phone,
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        # ذخیره در سشن
        request.session['temp_user_id'] = user.id
        request.session['otp_code'] = otp_code

        # ارسال پیامک
        sms_sent = send_otp_sms(phone, otp_code)

        if sms_sent:
            messages.success(request, f'✅ کد تایید به شماره {phone} ارسال شد')
        else:
            messages.warning(request, '⚠️ مشکلی در ارسال پیامک وجود دارد. کد زیر را وارد کنید:')
            print(f"🔑 کد تایید (برای تست): {otp_code}")

        return redirect('accounts_otp:verify_otp')

    return render(request, 'accounts_otp/register.html')


def verify_otp(request):
    user_id = request.session.get('temp_user_id')

    if not user_id:
        messages.error(request, 'لطفاً ابتدا ثبت نام کنید')
        return redirect('accounts_otp:register')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد')
        return redirect('accounts_otp:register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '')

        # بررسی OTP از دیتابیس
        try:
            otp_record = OTPCode.objects.filter(
                user=user,
                code=entered_otp,
                is_used=False,
                expires_at__gte=timezone.now()
            ).latest('created_at')

            # کد صحیح است
            otp_record.is_used = True
            otp_record.save()

            user.is_active = True
            user.save()
            login(request, user)

            # پاک کردن سشن
            request.session.pop('temp_user_id', None)
            request.session.pop('otp_code', None)

            messages.success(request, f'🎉 خوش آمدید {user.username}! ثبت نام شما با موفقیت انجام شد')
            return redirect('home-page')

        except OTPCode.DoesNotExist:
            # بررسی کد ذخیره شده در سشن (برای تست)
            correct_otp = request.session.get('otp_code')
            if correct_otp and entered_otp == correct_otp:
                user.is_active = True
                user.save()
                login(request, user)
                request.session.pop('temp_user_id', None)
                request.session.pop('otp_code', None)
                messages.success(request, f'🎉 خوش آمدید {user.username}! ثبت نام شما با موفقیت انجام شد')
                return redirect('home-page')

            messages.error(request, '❌ کد وارد شده اشتباه است یا منقضی شده است')

    return render(request, 'accounts_otp/verify_otp.html', {'phone': user.phone})


def resend_otp(request):
    user_id = request.session.get('temp_user_id')

    if not user_id:
        messages.error(request, 'لطفاً ابتدا ثبت نام کنید')
        return redirect('accounts_otp:register')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد')
        return redirect('accounts_otp:register')

    # ساخت کد جدید
    new_otp = generate_otp_code()
    request.session['otp_code'] = new_otp

    # ذخیره در دیتابیس
    OTPCode.objects.create(
        user=user,
        code=new_otp,
        phone=user.phone,
        expires_at=timezone.now() + timedelta(minutes=5),
        is_used=False
    )

    # ارسال پیامک
    sms_sent = send_otp_sms(user.phone, new_otp)

    if sms_sent:
        messages.success(request, f'✅ کد جدید به شماره {user.phone} ارسال شد')
    else:
        messages.warning(request, f'⚠️ کد جدید: {new_otp}')
        print(f"🔑 کد جدید: {new_otp}")

    return redirect('accounts_otp:verify_otp')


def forgot_password_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            messages.error(request, '❌ این شماره تلفن در سیستم ثبت نشده است.')
            return redirect('accounts_otp:forgot_password')

        otp_code = generate_otp_code()

        # حذف کدهای قبلی
        OTPCode.objects.filter(user=user, is_used=False).delete()

        # ایجاد کد جدید
        OTPCode.objects.create(
            user=user,
            code=otp_code,
            phone=phone,
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        # ارسال پیامک
        sms_sent = send_otp_sms(phone, otp_code)

        if sms_sent:
            messages.success(request, f'✅ کد تایید به شماره {phone} ارسال شد.')
        else:
            messages.warning(request, f'⚠️ کد تایید: {otp_code}')
            print(f"🔑 کد تایید: {otp_code}")

        request.session['reset_phone'] = phone

        return redirect('accounts_otp:verify_reset_otp')

    return render(request, 'accounts_otp/forgot-password.html')


def verify_reset_otp_view(request):
    phone = request.session.get('reset_phone')

    if not phone:
        messages.error(request, '❌ لطفاً ابتدا شماره تلفن خود را وارد کنید.')
        return redirect('accounts_otp:forgot_password')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')

        try:
            user = CustomUser.objects.get(phone=phone)
            otp_record = OTPCode.objects.filter(
                user=user,
                code=otp_code,
                is_used=False,
                expires_at__gte=timezone.now()
            ).latest('created_at')

            otp_record.is_used = True
            otp_record.save()

            request.session['reset_user_id'] = user.id

            messages.success(request, '✅ کد تایید صحیح است. رمز جدید خود را وارد کنید.')
            return redirect('accounts_otp:reset_password')

        except OTPCode.DoesNotExist:
            messages.error(request, '❌ کد تایید نامعتبر یا منقضی شده است.')

    return render(request, 'accounts_otp/verify-reset-otp.html', {'phone': phone})


def reset_password_view(request):
    user_id = request.session.get('reset_user_id')

    if not user_id:
        messages.error(request, '❌ لطفاً ابتدا کد تایید را وارد کنید.')
        return redirect('accounts_otp:forgot_password')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, '❌ کاربر یافت نشد.')
        return redirect('accounts_otp:forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or len(password) < 6:
            messages.error(request, '❌ رمز عبور باید حداقل 6 کاراکتر باشد.')
        elif password != confirm_password:
            messages.error(request, '❌ رمز عبور و تکرار آن مطابقت ندارند.')
        else:
            user.set_password(password)
            user.save()

            # پاک کردن سشن
            request.session.flush()

            messages.success(request, '✅ رمز عبور شما با موفقیت تغییر کرد. لطفاً با رمز جدید وارد شوید.')
            return redirect('accounts_otp:login')

    return render(request, 'accounts_otp/reset-password.html', {'phone': user.phone})
