from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("home_app.urls")),
    path("products/", include("product_app.urls")),
    path("blog/", include("blog_app.urls")),
    path("accounts/", include("accounts_app.urls")),
    path("accounts/otp/", include("accounts_otp.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
