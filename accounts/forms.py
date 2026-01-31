"""
User Registration and Authentication Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Registration form with role selection"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone', 'address',
                  'company_name', 'company_logo', 'gst_number', 'billing_address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'billing_address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'company_logo':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Make vendor fields optional initially
        self.fields['company_name'].required = False
        self.fields['company_logo'].required = False
        self.fields['gst_number'].required = False
        self.fields['billing_address'].required = False
