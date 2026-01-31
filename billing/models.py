"""
Billing and Payment Models
Handles: Invoices, Payments
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Invoice(models.Model):
    """
    Invoice for rental orders
    Can be paid in full or partially
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    rental_order = models.ForeignKey('rentals.RentalOrder', on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice details
    invoice_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    def get_remaining_balance(self):
        """Calculate remaining unpaid amount"""
        return self.total_amount - self.paid_amount
    
    def update_payment_status(self):
        """Update invoice status based on paid amount"""
        if self.paid_amount >= self.total_amount:
            self.status = 'PAID'
        elif self.paid_amount > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'DRAFT'
        self.save()
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        return timezone.now().date() > self.due_date and self.status != 'PAID'
    
    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    """
    Payment transactions
    Multiple payments can be made against one invoice
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('BANK', 'Bank Transfer'),
        ('UPI', 'UPI'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamp
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount} for {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        """Override save to update invoice paid amount"""
        super().save(*args, **kwargs)
        
        # Update invoice paid amount
        self.invoice.paid_amount = sum(
            payment.amount for payment in self.invoice.payments.all()
        )
        self.invoice.update_payment_status()
    
    class Meta:
        ordering = ['-payment_date']
