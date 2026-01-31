"""
Product Forms
"""
from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'image', 'quantity', 'daily_rate', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name == 'is_published':
                field.widget.attrs['class'] = 'form-check-input'
            elif field_name == 'image':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
