"""
System Configuration Models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RentalSettings(models.Model):
    """
    Global rental system configuration
    Singleton model - only one instance should exist
    """
    # Rental period settings
    min_rental_days = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum rental period in days"
    )
    max_rental_days = models.PositiveIntegerField(
        default=365,
        validators=[MinValueValidator(1)],
        help_text="Maximum rental period in days"
    )
    
    # Late fee settings
    late_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Late fee percentage per day"
    )
    
    # Tax settings
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tax rate percentage"
    )
    
    # Return reminder settings
    return_reminder_days = models.PositiveIntegerField(
        default=1,
        help_text="Days before return date to show reminder"
    )
    
    # Billing settings
    sync_billing_delivery_address = models.BooleanField(
        default=False,
        help_text="If enabled, billing and delivery addresses will be the same"
    )
    
    # Invoice settings
    invoice_due_days = models.PositiveIntegerField(
        default=7,
        help_text="Number of days until invoice is due"
    )
    
    # Site settings
    site_name = models.CharField(max_length=200, default="Rental Management System")
    support_email = models.EmailField(default="support@rental.com")
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rental Settings"
        verbose_name_plural = "Rental Settings"
    
    def __str__(self):
        return "Rental System Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create settings singleton"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
