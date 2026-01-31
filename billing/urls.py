"""
Billing URL Configuration
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Customer
    path('my-invoices/', views.MyInvoicesView.as_view(), name='my_invoices'),
    path('invoice/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoice/<int:invoice_id>/pay/', views.MakePaymentView.as_view(), name='make_payment'),
    path('invoice/<int:invoice_id>/download/', views.DownloadInvoiceView.as_view(), name='download_invoice'),
    
    # Vendor
    path('vendor/invoices/', views.VendorInvoicesView.as_view(), name='vendor_invoices'),
]
