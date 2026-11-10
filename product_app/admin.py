from django.contrib import admin
from .models import ProductModel, Category, Brand, ProductComment
from .models import Order, OrderItem
from .models import ProductImage


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'order']


class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'price', 'stock', 'in_stock', 'show_price']
    list_filter = ['in_stock', 'category', 'brand']
    search_fields = ['title']
    inlines = [ProductImageInline]

    def show_price(self, obj):
        return "{:,} تومان".format(obj.price)

    show_price.short_description = "قیمت"

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'category', 'brand', 'price', 'stock', 'in_stock')
        }),
        ('توضیحات', {
            'fields': ('short_description', 'long_description', 'specifications')
        }),
        ('تصاویر و گزینه‌ها', {
            'fields': ( 'colors', 'sizes')
        }),
    )


class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'product', 'text_preview', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')
    search_fields = ('user_name', 'text', 'product__title')

    def text_preview(self, obj):
        return obj.text[:50] + '…' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'متن دیدگاه'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'order']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(ProductComment, ProductCommentAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
