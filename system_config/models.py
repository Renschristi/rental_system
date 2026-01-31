"""
System Configuration Models
"""
from django.db import models
from decimal import Decimal


class SystemSettings(models.Model):
    """Singleton model for system-wide settings"""
    
    # Business Information
    business_name = models.CharField(max_length=200, default="Rental Management System")
    business_email = models.EmailField(default="admin@rental.com")
    business_phone = models.CharField(max_length=20, blank=True)
    
    # Rental Settings
    min_rental_days = models.PositiveIntegerField(default=1)
    max_rental_days = models.PositiveIntegerField(default=365)
    
    # Penalties
    late_return_penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    
    # Tax
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    tax_name = models.CharField(max_length=50, default="GST")
    
    # Security Deposit
    security_deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    
    # Currency
    currency_symbol = models.CharField(max_length=5, default="₹")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return "System Settings"
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
