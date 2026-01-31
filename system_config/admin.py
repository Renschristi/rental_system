from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Business Information', {
            'fields': ['business_name', 'business_email', 'business_phone']
        }),
        ('Rental Configuration', {
            'fields': ['min_rental_days', 'max_rental_days']
        }),
        ('Financial Settings', {
            'fields': ['tax_name', 'tax_rate', 'security_deposit_percentage', 'late_return_penalty_percentage']
        }),
        ('Currency', {
            'fields': ['currency_symbol']
        }),
    ]
    
    def has_add_permission(self, request):
        # Only one instance allowed
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Cannot delete settings
        return False
