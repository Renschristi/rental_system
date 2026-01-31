"""
Script to create sample rental periods for existing products
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_system.settings')
django.setup()

from products.models import Product
from products.rental_period_models import RentalPeriod
from decimal import Decimal

print("Adding rental periods to products...")

products = Product.objects.filter(is_published=True)

for product in products:
    base_daily_rate = product.daily_rate
    
    # Calculate different period rates
    hourly_rate = base_daily_rate / Decimal('24')  # Hourly rate
    weekly_rate = base_daily_rate * Decimal('6')   # 6 days rate for weekly (1 day discount)
    monthly_rate = base_daily_rate * Decimal('25') # 25 days rate for monthly (5 days discount)
    yearly_rate = base_daily_rate * Decimal('300') # 300 days rate for yearly (65 days discount)
    
    # Create rental periods
    periods = [
        {'period_type': 'HOURLY', 'price': hourly_rate.quantize(Decimal('0.01')), 'is_default': False},
        {'period_type': 'DAILY', 'price': base_daily_rate, 'is_default': True},
        {'period_type': 'WEEKLY', 'price': weekly_rate.quantize(Decimal('0.01')), 'is_default': False},
        {'period_type': 'MONTHLY', 'price': monthly_rate.quantize(Decimal('0.01')), 'is_default': False},
        {'period_type': 'YEARLY', 'price': yearly_rate.quantize(Decimal('0.01')), 'is_default': False},
    ]
    
    for period_data in periods:
        period, created = RentalPeriod.objects.get_or_create(
            product=product,
            period_type=period_data['period_type'],
            defaults={
                'price': period_data['price'],
                'is_default': period_data['is_default']
            }
        )
        if created:
            print(f"  ✓ {product.name}: {period.get_period_type_display()} - ₹{period.price}")

print(f"\n✓ Added rental periods to {products.count()} products")
print(f"Total rental periods: {RentalPeriod.objects.count()}")
