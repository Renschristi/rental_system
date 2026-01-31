"""
Products and Inventory Models
"""
from django.db import models
from django.conf import settings


class Category(models.Model):
    """Product categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Rentable Products
    Inventory is managed through quantity and reservations
    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory
    quantity = models.PositiveIntegerField(default=0, help_text="Total available quantity")
    
    # Pricing
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per day")
    
    # Status
    is_published = models.BooleanField(default=True, help_text="Show to customers (Admin only)")
    
    # Vendor
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    
    # Vendor restrictions - each vendor should only see products from their category
    # This helps in auto-splitting orders by vendor
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_available_quantity(self, start_date, end_date):
        """
        Calculate available quantity for a date range
        Check overlapping reservations and return remaining quantity
        """
        from rentals.models import RentalOrderLine
        
        # Get all confirmed/active rental lines that overlap with the requested period
        overlapping_rentals = RentalOrderLine.objects.filter(
            product=self,
            rental_order__status__in=['CONFIRMED', 'ACTIVE'],
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        
        # Sum up reserved quantities
        reserved_qty = sum(line.quantity for line in overlapping_rentals)
        
        # Return available quantity
        return self.quantity - reserved_qty
    
    def is_available(self, start_date, end_date, requested_qty=1):
        """Check if product is available for rental in given period"""
        available = self.get_available_quantity(start_date, end_date)
        return available >= requested_qty
    
    class Meta:
        ordering = ['-created_at']
