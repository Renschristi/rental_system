"""
Coupon System Models
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Coupon(models.Model):
    """
    Discount coupons for rentals
    """
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='PERCENTAGE')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage or fixed amount")
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Usage limits
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    uses_count = models.PositiveIntegerField(default=0)
    
    # Restrictions
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum discount amount (for percentage coupons)"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    for_new_users = models.BooleanField(default=False, help_text="Only for first-time users")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'PERCENTAGE' else '₹'}"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses == 0 or self.uses_count < self.max_uses)
        )
    
    def calculate_discount(self, order_total):
        """Calculate discount amount for given order total"""
        if not self.is_valid():
            return Decimal('0')
        
        if order_total < self.min_order_amount:
            return Decimal('0')
        
        if self.discount_type == 'PERCENTAGE':
            discount = order_total * (self.discount_value / Decimal('100'))
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value
        
        return min(discount, order_total)
    
    class Meta:
        ordering = ['-created_at']


class CouponUsage(models.Model):
    """
    Track coupon usage by users
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    rental_order = models.ForeignKey('rentals.RentalOrder', on_delete=models.CASCADE, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.coupon.code} - ₹{self.discount_amount}"
    
    class Meta:
        ordering = ['-used_at']
