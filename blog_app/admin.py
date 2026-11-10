from django.contrib import admin
from .models import BlogPost, BlogComment


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'views_count', 'published_at']
    list_filter = ['status', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('محتوا', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('آمار', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )


class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'email', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'comment']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = "تایید نظرات انتخاب شده"


admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
