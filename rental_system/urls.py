"""
Main URL Configuration for rental_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboards.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('rentals/', include('rentals.urls')),
    path('billing/', include('billing.urls')),
    path('', include('static_pages.urls')),  # Terms, About, Contact
    path('', include('system_config.urls')),  # System Settings
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
