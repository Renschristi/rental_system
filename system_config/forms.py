from django import forms
from .models import SystemSettings


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = [
            'business_name', 'business_email', 'business_phone',
            'min_rental_days', 'max_rental_days',
            'late_return_penalty_percentage',
            'tax_name', 'tax_rate',
            'security_deposit_percentage',
            'currency_symbol'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'business_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'min_rental_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'max_rental_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'late_return_penalty_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'security_deposit_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control'}),
        }
