"""
Product Views - Public and Vendor
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Product, Category
from .forms import ProductForm


class ProductListView(ListView):
    """Public product listing page"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_published=True)
        
        # Filter by category if provided
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Product detail page with rental configuration"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_published=True)


# Vendor Views

class VendorProductListView(LoginRequiredMixin, ListView):
    """Vendor's product management list"""
    model = Product
    template_name = 'products/vendor_product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Only show vendor's own products
        return Product.objects.filter(vendor=self.request.user)


class VendorProductCreateView(LoginRequiredMixin, CreateView):
    """Create new product (Vendor only)"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:vendor_products')
    
    def form_valid(self, form):
        form.instance.vendor = self.request.user
        # Only admin can publish products
        if not self.request.user.is_admin():
            form.instance.is_published = False
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)


class VendorProductUpdateView(LoginRequiredMixin, UpdateView):
    """Update product (Vendor only)"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:vendor_products')
    
    def get_queryset(self):
        # Only allow vendor to edit their own products
        return Product.objects.filter(vendor=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)
