"""
Billing Forms
"""
from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    """Form for making payments"""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Make transaction_id and notes optional
        self.fields['transaction_id'].required = False
        self.fields['notes'].required = False
