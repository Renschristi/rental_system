from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'daily_rate', 'is_published', 'vendor', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_published']
