# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser, OTPCode
#
#
# # تنظیم نمایش کاربران در ادمین
# class CustomUserAdmin(UserAdmin):
#     # حذف email و اضافه کردن phone
#     list_display = ('phone', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
#     list_filter = ('is_staff', 'is_active', 'date_joined')
#     search_fields = ('phone', 'username', 'first_name', 'last_name')
#     ordering = ('-date_joined',)
#
#     fieldsets = (
#         (None, {'fields': ('phone', 'password')}),
#         ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'username')}),
#         ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#         ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('phone', 'password1', 'password2'),
#         }),
#     )
#
#
# # ثبت مدل CustomUser با تنظیمات سفارشی
# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(OTPCode)
