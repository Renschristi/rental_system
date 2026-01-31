"""
Update Script - Add vendor information to existing users
Run: python manage.py shell < update_vendor_info.py
"""

from accounts.models import User

print("=" * 60)
print("UPDATING VENDOR INFORMATION")
print("=" * 60)

# Update vendor1 with company info
try:
    vendor1 = User.objects.get(username='vendor1')
    vendor1.company_name = "TechRent Solutions"
    vendor1.gst_number = "GST123456789"
    vendor1.billing_address = "123 Business Park, Tech City, TC 12345"
    vendor1.save()
    print("✓ Updated vendor1 with company information")
except User.DoesNotExist:
    print("✗ vendor1 not found")

# Update admin with company info
try:
    admin = User.objects.get(username='admin')
    admin.company_name = "Rental Management Corp"
    admin.gst_number = "GST987654321"
    admin.billing_address = "456 Admin Tower, Business District, BD 67890"
    admin.save()
    print("✓ Updated admin with company information")
except User.DoesNotExist:
    print("✗ admin not found")

# Update customer1 with billing address
try:
    customer1 = User.objects.get(username='customer1')
    customer1.billing_address = "789 Customer Street, Residential Area, RA 11111"
    customer1.save()
    print("✓ Updated customer1 with billing address")
except User.DoesNotExist:
    print("✗ customer1 not found")

print("\n" + "=" * 60)
print("UPDATE COMPLETE!")
print("=" * 60)
print("\nNew Features Added:")
print("  - Vendor company logos (upload via admin)")
print("  - GST/Tax ID numbers")
print("  - Billing addresses")
print("  - Rental order filters (Paid, Returning Soon)")
print("  - Admin-only product publishing")
print("  - Vendor logos on PDF invoices")
print("\nNext Steps:")
print("  1. Login as vendor and upload company logo")
print("  2. Test filtered views in Vendor Rentals")
print("  3. Generate invoice PDF to see vendor logo")
