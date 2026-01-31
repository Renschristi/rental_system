"""
Update product prices from USD to INR (Rupees)
Using conversion rate: 1 USD = 83 INR (approximate)
"""

from products.models import Product
from decimal import Decimal

# Conversion rate from USD to INR
USD_TO_INR = Decimal('83.00')

print("Updating product prices from USD to INR...")
print("-" * 60)

products = Product.objects.all()

for product in products:
    old_price = product.daily_rate
    # Convert USD to INR and round to 2 decimal places
    new_price = (old_price * USD_TO_INR).quantize(Decimal('0.01'))
    
    product.daily_rate = new_price
    product.save()
    
    print(f"{product.name}:")
    print(f"  Old: ${old_price}/day")
    print(f"  New: ₹{new_price}/day")
    print()

print("-" * 60)
print(f"Successfully updated {products.count()} products!")
print("\nNote: All existing rentals and invoices will show updated prices.")
print("Historical data remains unchanged in the database.")
