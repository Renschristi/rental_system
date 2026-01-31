"""
Wishlist Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from products.wishlist_models import Wishlist


class AddToWishlistView(LoginRequiredMixin, View):
    """Add product to wishlist"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_published=True)
        
        # Create or get wishlist item
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            messages.success(request, f'{product.name} added to wishlist!')
        else:
            messages.info(request, f'{product.name} is already in your wishlist.')
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'created': created})
        
        return redirect('products:product_detail', pk=product_id)


class RemoveFromWishlistView(LoginRequiredMixin, View):
    """Remove product from wishlist"""
    
    def post(self, request, wishlist_id):
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        
        messages.success(request, f'{product_name} removed from wishlist.')
        return redirect('products:wishlist')


class WishlistView(LoginRequiredMixin, ListView):
    """Display user's wishlist"""
    model = Wishlist
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product', 'product__category')
