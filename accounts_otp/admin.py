from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTPCode


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'email', 'get_full_address', 'province', 'city', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'province', 'city')
    search_fields = ('username', 'phone', 'email', 'province', 'city', 'address', 'postal_code', 'receiver_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تماس', {
            'fields': ('phone',)
        }),
        ('اطلاعات آدرس', {
            'fields': ('province', 'city', 'address', 'postal_code', 'receiver_name'),
            'classes': ('wide',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تماس', {
            'fields': ('phone',)
        }),
        ('اطلاعات آدرس (اختیاری)', {
            'fields': ('province', 'city', 'address', 'postal_code', 'receiver_name'),
            'classes': ('wide',),
        }),
    )

    def get_full_address(self, obj):
        """نمایش آدرس کامل در لیست ادمین"""
        if obj.address:
            return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
        return '—'

    get_full_address.short_description = 'آدرس کامل'
    get_full_address.admin_order_field = 'address'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTPCode)
