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
        
        # Filter by brand
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand=brand)
        
        # Filter by color
        color = self.request.GET.get('color')
        if color:
            queryset = queryset.filter(color=color)
        
        # Filter by price range
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(daily_rate__gte=price_min)
        if price_max:
            queryset = queryset.filter(daily_rate__lte=price_max)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.select_related('category', 'vendor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        # Get distinct brands and colors for filters
        context['brands'] = Product.objects.filter(
            is_published=True, 
            brand__isnull=False
        ).exclude(brand='').values_list('brand', flat=True).distinct().order_by('brand')
        
        context['colors'] = Product.objects.filter(
            is_published=True,
            color__isnull=False
        ).exclude(color='').values_list('color', flat=True).distinct().order_by('color')
        
        return context


class ProductDetailView(DetailView):
    """Product detail page with rental configuration"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_published=True).prefetch_related(
            'rental_periods',
            'variants',
            'attribute_lines__attribute',
            'attribute_lines__attribute_value'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        import json
        
        context['today'] = timezone.now().date()
        
        # Prepare variant data for JavaScript
        if self.object.has_variants:
            variants_data = []
            for variant in self.object.variants.filter(is_active=True):
                variants_data.append({
                    'id': variant.id,
                    'name': str(variant),
                    'price': float(variant.get_final_price()),
                    'quantity': variant.quantity,
                    'attributes': [
                        {
                            'attribute_id': str(pav.attribute_value.attribute.id),
                            'value_id': str(pav.attribute_value.id)
                        }
                        for pav in variant.attribute_values.all()
                    ]
                })
            context['variants_json'] = json.dumps(variants_data)
            
            # Get required attribute IDs
            attribute_ids = list(self.object.attribute_lines.values_list(
                'attribute_id', flat=True
            ).distinct())
            context['required_attributes'] = json.dumps([str(id) for id in attribute_ids])
        else:
            context['variants_json'] = '[]'
            context['required_attributes'] = '[]'
        
        return context


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
