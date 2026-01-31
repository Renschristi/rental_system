"""
User and Role Management Models
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access
    Roles: CUSTOMER, VENDOR, ADMIN
    """
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('VENDOR', 'Vendor'),
        ('ADMIN', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_customer(self):
        return self.role == 'CUSTOMER'
    
    def is_vendor(self):
        return self.role == 'VENDOR'
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
