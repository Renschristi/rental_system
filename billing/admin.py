from django.contrib import admin
from .models import Invoice, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'status', 'total_amount', 'paid_amount', 'created_at', 'due_date']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'customer__username']
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
