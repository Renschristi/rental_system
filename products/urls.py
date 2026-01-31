"""
Products URL Configuration
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Vendor
    path('vendor/products/', views.VendorProductListView.as_view(), name='vendor_products'),
    path('vendor/products/create/', views.VendorProductCreateView.as_view(), name='product_create'),
    path('vendor/products/<int:pk>/edit/', views.VendorProductUpdateView.as_view(), name='product_edit'),
]
