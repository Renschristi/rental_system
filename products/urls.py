"""
Products URL Configuration
"""
from django.urls import path
from . import views
from .wishlist_views import AddToWishlistView, RemoveFromWishlistView, WishlistView

app_name = 'products'

urlpatterns = [
    # Public
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Wishlist
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:product_id>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    
    # Vendor
    path('vendor/products/', views.VendorProductListView.as_view(), name='vendor_products'),
    path('vendor/products/create/', views.VendorProductCreateView.as_view(), name='product_create'),
    path('vendor/products/<int:pk>/edit/', views.VendorProductUpdateView.as_view(), name='product_edit'),
]
