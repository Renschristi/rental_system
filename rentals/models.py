"""
Rental Management Models
Handles: Quotations, Reservations, Rental Orders, Pickup, Returns
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Quotation(models.Model):
    """
    Shopping cart / Quotation
    Status: DRAFT (editable) or CONFIRMED (converted to rental order)
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quotations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Quotation #{self.id} - {self.customer.username}"
    
    def get_total(self):
        """Calculate total quotation amount"""
        return sum(line.get_subtotal() for line in self.lines.all())
    
    def can_confirm(self):
        """Check if quotation can be confirmed (all items available)"""
        for line in self.lines.all():
            if not line.product.is_available(line.start_date, line.end_date, line.quantity):
                return False
        return self.lines.exists() and self.status == 'DRAFT'
    
    class Meta:
        ordering = ['-created_at']


class QuotationLine(models.Model):
    """
    Individual items in a quotation
    """
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # Rental period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Pricing (snapshot at quotation time)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    def get_duration_days(self):
        """Calculate rental duration in days"""
        delta = self.end_date - self.start_date
        return max(delta.days, 1)  # Minimum 1 day
    
    def get_subtotal(self):
        """Calculate line subtotal"""
        return self.daily_rate * self.quantity * self.get_duration_days()
    
    class Meta:
        unique_together = ['quotation', 'product']


class RentalOrder(models.Model):
    """
    Confirmed Rental Order
    Created from quotation confirmation
    Status flow: CONFIRMED -> ACTIVE -> RETURNED
    """
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('ACTIVE', 'Active (Picked Up)'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rental_orders')
    quotation = models.OneToOneField(Quotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='rental_order')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    
    # Order reference
    order_number = models.CharField(max_length=20, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    
    # Late fees
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Rental Order {self.order_number}"
    
    def get_total(self):
        """Calculate total order amount including late fees"""
        subtotal = sum(line.get_subtotal() for line in self.lines.all())
        return subtotal + self.late_fee
    
    def mark_as_active(self):
        """Mark order as active (picked up)"""
        self.status = 'ACTIVE'
        self.pickup_date = timezone.now()
        self.save()
    
    def calculate_late_fees(self):
        """
        Calculate late fees based on return dates
        Apply late fee if actual return date > planned end date
        """
        if not self.return_date:
            return Decimal('0')
        
        total_late_fee = Decimal('0')
        
        for line in self.lines.all():
            # Check if returned late
            if self.return_date.date() > line.end_date:
                days_late = (self.return_date.date() - line.end_date).days
                # Late fee: X% of daily rate per day late
                late_fee_rate = Decimal(str(settings.RENTAL_LATE_FEE_PERCENT)) / 100
                line_late_fee = line.daily_rate * line.quantity * days_late * late_fee_rate
                total_late_fee += line_late_fee
        
        return total_late_fee
    
    def mark_as_returned(self):
        """Mark order as returned and calculate late fees"""
        self.status = 'RETURNED'
        self.return_date = timezone.now()
        self.late_fee = self.calculate_late_fees()
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class RentalOrderLine(models.Model):
    """
    Individual rental items in an order
    These lines create the reservation (lock inventory)
    """
    rental_order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    # Rental period (copied from quotation)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Pricing snapshot
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.start_date} to {self.end_date})"
    
    def get_duration_days(self):
        """Calculate rental duration in days"""
        delta = self.end_date - self.start_date
        return max(delta.days, 1)
    
    def get_subtotal(self):
        """Calculate line subtotal"""
        return self.daily_rate * self.quantity * self.get_duration_days()
