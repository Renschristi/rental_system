from django.contrib import admin
from .models import Category, Product
from .wishlist_models import Wishlist
from .rental_period_models import RentalPeriod
from .variant_models import ProductAttribute, ProductAttributeValue, ProductVariant, ProductVariantAttributeValue, ProductAttributeLine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class RentalPeriodInline(admin.TabularInline):
    model = RentalPeriod
    extra = 1
    fields = ['period_type', 'price', 'is_default']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'daily_rate', 'is_published', 'vendor', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_published']
    inlines = [RentalPeriodInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']


@admin.register(RentalPeriod)
class RentalPeriodAdmin(admin.ModelAdmin):
    list_display = ['product', 'period_type', 'price', 'is_default']
    list_filter = ['period_type', 'is_default']
    search_fields = ['product__name']


# Product Attributes and Variants

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ['value', 'color_code', 'extra_price']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_type', 'created_at']
    list_filter = ['display_type']
    search_fields = ['name']
    inlines = [ProductAttributeValueInline]


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'color_code', 'extra_price']
    list_filter = ['attribute']
    search_fields = ['value', 'attribute__name']


class ProductVariantAttributeValueInline(admin.TabularInline):
    model = ProductVariantAttributeValue
    extra = 1
    fields = ['attribute_value']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'quantity', 'price_adjustment', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['sku', 'product__name']
    inlines = [ProductVariantAttributeValueInline]


@admin.register(ProductAttributeLine)
class ProductAttributeLineAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'required']
    list_filter = ['attribute', 'required']
    search_fields = ['product__name', 'attribute__name']
