from django.contrib import admin
from .models import Quotation, QuotationLine, RentalOrder, RentalOrderLine, Coupon, CouponUsage


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 0


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'applied_coupon', 'discount_amount', 'created_at', 'confirmed_at']
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


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'uses_count', 'max_uses', 'is_active', 'for_new_users']
    list_filter = ['discount_type', 'is_active', 'for_new_users', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['uses_count']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'rental_order', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__username']
