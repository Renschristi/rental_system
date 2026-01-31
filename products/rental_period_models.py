"""
Rental Period Configuration Model
"""
from django.db import models
from decimal import Decimal


class RentalPeriod(models.Model):
    """
    Different rental period options (Hourly, Daily, Weekly, Monthly)
    """
    PERIOD_TYPE_CHOICES = [
        ('HOURLY', 'Per Hour'),
        ('DAILY', 'Per Day'),
        ('WEEKLY', 'Per Week'),
        ('MONTHLY', 'Per Month'),
        ('YEARLY', 'Per Year'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='rental_periods')
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this period")
    is_default = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['product', 'period_type']
        ordering = ['product', 'period_type']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_period_type_display()} - ₹{self.price}"
    
    def calculate_price(self, days):
        """
        Calculate price based on rental days
        """
        if self.period_type == 'HOURLY':
            # Assume 24 hours per day
            return self.price * Decimal(str(days * 24))
        elif self.period_type == 'DAILY':
            return self.price * Decimal(str(days))
        elif self.period_type == 'WEEKLY':
            weeks = Decimal(str(days)) / Decimal('7')
            return self.price * weeks
        elif self.period_type == 'MONTHLY':
            months = Decimal(str(days)) / Decimal('30')
            return self.price * months
        elif self.period_type == 'YEARLY':
            years = Decimal(str(days)) / Decimal('365')
            return self.price * years
        return Decimal('0')
