"""
Product Attributes and Variants Models
Allows products to have multiple attributes (Brand, Color, Size) with different values
"""
from django.db import models
from products.models import Product


class ProductAttribute(models.Model):
    """
    Defines types of attributes (e.g., Brand, Color, Size)
    """
    name = models.CharField(max_length=100, unique=True)
    display_type = models.CharField(
        max_length=20,
        choices=[
            ('RADIO', 'Radio Buttons'),
            ('PILLS', 'Pills'),
            ('SELECT', 'Dropdown'),
            ('COLOR', 'Color Swatches'),
        ],
        default='RADIO'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class ProductAttributeValue(models.Model):
    """
    Individual values for an attribute (e.g., Red, Blue for Color attribute)
    """
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color code for color attributes")
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Additional price for this variant")
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"
    
    class Meta:
        ordering = ['attribute', 'value']
        unique_together = ['attribute', 'value']


class ProductVariant(models.Model):
    """
    Specific combination of attributes for a product
    Example: MacBook Pro - Silver, 512GB
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Price difference from base product (can be negative)"
    )
    image = models.ImageField(upload_to='product_variants/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        values = ", ".join([pav.attribute_value.value for pav in self.attribute_values.all()])
        return f"{self.product.name} - {values}"
    
    def get_final_price(self):
        """Calculate final price including adjustments"""
        return self.product.daily_rate + self.price_adjustment
    
    def is_available(self, start_date, end_date, quantity=1):
        """Check variant availability for date range"""
        from rentals.models import RentalOrderLine
        
        # Get overlapping reservations for this variant
        overlapping = RentalOrderLine.objects.filter(
            product_variant=self,
            rental_order__status__in=['CONFIRMED', 'ACTIVE'],
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        
        reserved_quantity = sum(line.quantity for line in overlapping)
        available = self.quantity - reserved_quantity
        
        return available >= quantity
    
    class Meta:
        unique_together = ['product', 'sku']


class ProductVariantAttributeValue(models.Model):
    """
    Links variants to their attribute values
    Example: Variant "MacBook Pro - Silver, 512GB" has values "Silver" and "512GB"
    """
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute_value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"
    
    class Meta:
        unique_together = ['variant', 'attribute_value']


class ProductAttributeLineQuerySet(models.QuerySet):
    def for_product(self, product):
        return self.filter(product=product).select_related('attribute').prefetch_related('attribute__values')


class ProductAttributeLine(models.Model):
    """
    Assigns attributes to products
    Example: Product "MacBook Pro" has attributes "Color" and "Storage"
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_lines')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    required = models.BooleanField(default=True, help_text="Must customer select this attribute?")
    
    objects = ProductAttributeLineQuerySet.as_manager()
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"
    
    def get_available_values(self):
        """Get all available values for this attribute on this product"""
        return self.attribute.values.all()
    
    class Meta:
        unique_together = ['product', 'attribute']
        ordering = ['product', 'attribute']
