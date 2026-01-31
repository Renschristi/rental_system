from django.contrib import admin
from .models import Quotation, QuotationLine, RentalOrder, RentalOrderLine


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 0


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at', 'confirmed_at']
    list_filter = ['status', 'created_at']
    inlines = [QuotationLineInline]


class RentalOrderLineInline(admin.TabularInline):
    model = RentalOrderLine
    extra = 0


@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'created_at', 'pickup_date', 'return_date']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__username']
    inlines = [RentalOrderLineInline]
