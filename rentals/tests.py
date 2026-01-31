from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from products.models import Product, Category
from .models import Quotation, QuotationLine, RentalOrder

User = get_user_model()


class ReservationAlgorithmTest(TestCase):
    """
    Critical tests for the reservation algorithm
    """
    
    def setUp(self):
        # Create test users
        self.customer = User.objects.create_user(
            username='testcustomer',
            password='test123',
            role='CUSTOMER'
        )
        
        self.vendor = User.objects.create_user(
            username='testvendor',
            password='test123',
            role='VENDOR'
        )
        
        # Create test product
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Laptop',
            category=self.category,
            description='Test product',
            quantity=2,
            daily_rate=50.00,
            vendor=self.vendor,
            is_published=True
        )
    
    def test_availability_calculation_no_rentals(self):
        """Test availability with no existing rentals"""
        start = date.today()
        end = start + timedelta(days=5)
        
        available = self.product.get_available_quantity(start, end)
        self.assertEqual(available, 2)
    
    def test_availability_with_overlapping_rental(self):
        """Test availability calculation with overlapping rental"""
        # Create existing rental
        start1 = date.today()
        end1 = start1 + timedelta(days=7)
        
        quotation = Quotation.objects.create(
            customer=self.customer,
            status='CONFIRMED'
        )
        
        rental = RentalOrder.objects.create(
            customer=self.customer,
            quotation=quotation,
            order_number='TEST-001',
            status='CONFIRMED'
        )
        
        from .models import RentalOrderLine
        RentalOrderLine.objects.create(
            rental_order=rental,
            product=self.product,
            quantity=1,
            start_date=start1,
            end_date=end1,
            daily_rate=50.00
        )
        
        # Check availability for overlapping period
        start2 = start1 + timedelta(days=3)
        end2 = start2 + timedelta(days=5)
        
        available = self.product.get_available_quantity(start2, end2)
        self.assertEqual(available, 1)  # 2 total - 1 reserved = 1 available
    
    def test_no_overlap_different_periods(self):
        """Test that non-overlapping periods don't affect availability"""
        # Create existing rental
        start1 = date.today()
        end1 = start1 + timedelta(days=5)
        
        quotation = Quotation.objects.create(
            customer=self.customer,
            status='CONFIRMED'
        )
        
        rental = RentalOrder.objects.create(
            customer=self.customer,
            quotation=quotation,
            order_number='TEST-002',
            status='CONFIRMED'
        )
        
        from .models import RentalOrderLine
        RentalOrderLine.objects.create(
            rental_order=rental,
            product=self.product,
            quantity=1,
            start_date=start1,
            end_date=end1,
            daily_rate=50.00
        )
        
        # Check availability for non-overlapping period (after existing rental)
        start2 = end1 + timedelta(days=1)
        end2 = start2 + timedelta(days=5)
        
        available = self.product.get_available_quantity(start2, end2)
        self.assertEqual(available, 2)  # Should be fully available


# TODO: Add more tests:
# - Test concurrent confirmations
# - Test late fee calculation
# - Test partial payment updates
# - Test status transitions
