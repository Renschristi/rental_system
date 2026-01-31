"""
Script to create sample coupons for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_system.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from rentals.models import Coupon

# Create sample coupons
coupons_data = [
    {
        'code': 'WELCOME10',
        'description': 'Welcome offer - 10% off for new users',
        'discount_type': 'PERCENTAGE',
        'discount_value': 10,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=365),
        'max_uses': 100,
        'for_new_users': True,
        'min_order_amount': 500,
        'is_active': True,
    },
    {
        'code': 'SAVE20',
        'description': 'Save ₹20 on orders above ₹1000',
        'discount_type': 'FIXED',
        'discount_value': 20,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=30),
        'max_uses': 0,  # unlimited
        'for_new_users': False,
        'min_order_amount': 1000,
        'is_active': True,
    },
    {
        'code': 'MEGA25',
        'description': 'Mega sale - 25% off on all products',
        'discount_type': 'PERCENTAGE',
        'discount_value': 25,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=7),
        'max_uses': 50,
        'for_new_users': False,
        'min_order_amount': 1500,
        'max_discount_amount': 500,
        'is_active': True,
    },
    {
        'code': 'FIRSTORDER',
        'description': 'First order special - ₹100 off',
        'discount_type': 'FIXED',
        'discount_value': 100,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=90),
        'max_uses': 0,
        'for_new_users': True,
        'min_order_amount': 2000,
        'is_active': True,
    },
    {
        'code': 'FLASH15',
        'description': 'Flash sale - 15% off for 24 hours',
        'discount_type': 'PERCENTAGE',
        'discount_value': 15,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(hours=24),
        'max_uses': 20,
        'for_new_users': False,
        'min_order_amount': 800,
        'is_active': True,
    },
]

print("Creating sample coupons...")
for coupon_data in coupons_data:
    coupon, created = Coupon.objects.get_or_create(
        code=coupon_data['code'],
        defaults=coupon_data
    )
    if created:
        print(f"✓ Created: {coupon.code} - {coupon.description}")
    else:
        print(f"• Already exists: {coupon.code}")

print(f"\n{Coupon.objects.count()} total coupons in database")
print("\nAvailable coupons:")
for coupon in Coupon.objects.all():
    status = "ACTIVE" if coupon.is_valid() else "INACTIVE"
    print(f"  {coupon.code} ({status}) - {coupon.description}")
