"""
Setup Script - Creates initial data for the rental system
Run: python manage.py shell < setup_data.py
"""

from accounts.models import User
from products.models import Category, Product

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@rental.com',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("✓ Admin user created (username: admin, password: admin123)")

# Create vendor user
vendor, created = User.objects.get_or_create(
    username='vendor1',
    defaults={
        'email': 'vendor@rental.com',
        'role': 'VENDOR',
        'phone': '123-456-7890',
        'address': '123 Vendor Street'
    }
)
if created:
    vendor.set_password('vendor123')
    vendor.save()
    print("✓ Vendor user created (username: vendor1, password: vendor123)")

# Create customer user
customer, created = User.objects.get_or_create(
    username='customer1',
    defaults={
        'email': 'customer@rental.com',
        'role': 'CUSTOMER',
        'phone': '098-765-4321',
        'address': '456 Customer Avenue'
    }
)
if created:
    customer.set_password('customer123')
    customer.save()
    print("✓ Customer user created (username: customer1, password: customer123)")

# Create categories
categories_data = [
    {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
    {'name': 'Tools', 'description': 'Power tools and equipment'},
    {'name': 'Vehicles', 'description': 'Cars, bikes, and other vehicles'},
    {'name': 'Events', 'description': 'Event equipment and supplies'},
    {'name': 'Sports', 'description': 'Sports equipment and gear'},
]

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"✓ Category created: {category.name}")

# Create sample products
electronics = Category.objects.get(name='Electronics')
tools = Category.objects.get(name='Tools')
vehicles = Category.objects.get(name='Vehicles')

products_data = [
    {
        'name': 'MacBook Pro 16"',
        'category': electronics,
        'description': 'High-performance laptop for professionals. Perfect for video editing, development, and design work.',
        'quantity': 5,
        'daily_rate': 50.00,
        'vendor': vendor
    },
    {
        'name': 'Canon DSLR Camera',
        'category': electronics,
        'description': 'Professional camera for photography and videography. Includes lens kit.',
        'quantity': 3,
        'daily_rate': 35.00,
        'vendor': vendor
    },
    {
        'name': 'Power Drill Set',
        'category': tools,
        'description': 'Complete power drill set with multiple bits and accessories.',
        'quantity': 10,
        'daily_rate': 15.00,
        'vendor': vendor
    },
    {
        'name': 'Honda Sedan',
        'category': vehicles,
        'description': 'Comfortable sedan for city and highway driving. Automatic transmission, AC.',
        'quantity': 2,
        'daily_rate': 80.00,
        'vendor': vendor
    },
    {
        'name': 'Mountain Bike',
        'category': vehicles,
        'description': 'High-quality mountain bike for trails and off-road adventures.',
        'quantity': 8,
        'daily_rate': 20.00,
        'vendor': vendor
    },
]

for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        name=prod_data['name'],
        vendor=prod_data['vendor'],
        defaults={
            'category': prod_data['category'],
            'description': prod_data['description'],
            'quantity': prod_data['quantity'],
            'daily_rate': prod_data['daily_rate'],
            'is_published': True
        }
    )
    if created:
        print(f"✓ Product created: {product.name}")

print("\n" + "="*50)
print("Setup Complete!")
print("="*50)
print("\nTest Users:")
print("  Admin:    username=admin,     password=admin123")
print("  Vendor:   username=vendor1,   password=vendor123")
print("  Customer: username=customer1, password=customer123")
print("\nRun the server: python manage.py runserver")
print("Access at: http://localhost:8000")
