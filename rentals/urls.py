"""
Rentals URL Configuration
"""
from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    # Customer
    path('quotation/add/<int:product_id>/', views.AddToQuotationView.as_view(), name='add_to_quotation'),
    path('quotation/', views.ViewQuotationView.as_view(), name='view_quotation'),
    path('quotation/remove/<int:line_id>/', views.RemoveFromQuotationView.as_view(), name='remove_from_quotation'),
    path('quotation/confirm/', views.ConfirmQuotationView.as_view(), name='confirm_quotation'),
    
    path('my-rentals/', views.MyRentalsView.as_view(), name='my_rentals'),
    path('rental/<int:pk>/', views.RentalDetailView.as_view(), name='rental_detail'),
    
    # Vendor
    path('vendor/rentals/', views.VendorRentalListView.as_view(), name='vendor_rentals'),
    path('vendor/rental/<int:pk>/pickup/', views.PickupRentalView.as_view(), name='pickup_rental'),
    path('vendor/rental/<int:pk>/return/', views.ReturnRentalView.as_view(), name='return_rental'),
]
