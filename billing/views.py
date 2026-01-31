"""
Billing and Payment Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from decimal import Decimal

from .models import Invoice, Payment
from .forms import PaymentForm

# For PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


class MyInvoicesView(LoginRequiredMixin, ListView):
    """Customer's invoices"""
    model = Invoice
    template_name = 'billing/my_invoices.html'
    context_object_name = 'invoices'
    
    def get_queryset(self):
        return Invoice.objects.filter(customer=self.request.user).order_by('-created_at')


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Invoice detail with payment history"""
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        # Customers can only view their own invoices
        if self.request.user.is_customer():
            return Invoice.objects.filter(customer=self.request.user)
        # Vendors can view invoices for rentals of their products
        elif self.request.user.is_vendor():
            return Invoice.objects.filter(rental_order__lines__product__vendor=self.request.user).distinct()
        # Admins can view all
        return Invoice.objects.all()


class MakePaymentView(LoginRequiredMixin, View):
    """Process payment for invoice"""
    
    @transaction.atomic
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        form = PaymentForm()
        
        context = {
            'invoice': invoice,
            'form': form,
            'remaining_balance': invoice.get_remaining_balance()
        }
        return render(request, 'billing/make_payment.html', context)
    
    @transaction.atomic
    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            
            # Validate payment amount
            remaining = invoice.get_remaining_balance()
            if payment.amount > remaining:
                messages.error(request, f'Payment amount cannot exceed remaining balance (₹{remaining}).')
                return render(request, 'billing/make_payment.html', {
                    'invoice': invoice,
                    'form': form,
                    'remaining_balance': remaining
                })
            
            if payment.amount <= 0:
                messages.error(request, 'Payment amount must be greater than zero.')
                return render(request, 'billing/make_payment.html', {
                    'invoice': invoice,
                    'form': form,
                    'remaining_balance': remaining
                })
            
            payment.save()  # This automatically updates invoice status
            
            messages.success(request, f'Payment of ₹{payment.amount} processed successfully!')
            return redirect('billing:invoice_detail', pk=invoice.id)
        
        context = {
            'invoice': invoice,
            'form': form,
            'remaining_balance': invoice.get_remaining_balance()
        }
        return render(request, 'billing/make_payment.html', context)


class DownloadInvoiceView(LoginRequiredMixin, View):
    """Generate and download invoice PDF"""
    
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id, customer=request.user)
        
        # Get vendor logo if available (from first product's vendor)
        vendor_logo = None
        first_line = invoice.rental_order.lines.first()
        if first_line and first_line.product.vendor.company_logo:
            vendor_logo = first_line.product.vendor.company_logo
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        
        # Create the PDF object
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        # Add vendor logo if available
        y_start = height - 1 * inch
        if vendor_logo:
            try:
                from PIL import Image
                import os
                logo_path = vendor_logo.path
                if os.path.exists(logo_path):
                    # Draw logo in top right
                    p.drawImage(logo_path, width - 2.5 * inch, height - 1.5 * inch, 
                               width=1.5 * inch, height=1 * inch, preserveAspectRatio=True)
            except Exception as e:
                pass  # Skip logo if there's an error
        
        # Title
        p.setFont("Helvetica-Bold", 20)
        p.drawString(1 * inch, y_start, "RENTAL INVOICE")
        
        # Invoice details
        p.setFont("Helvetica", 12)
        y = height - 1.5 * inch
        
        p.drawString(1 * inch, y, f"Invoice Number: {invoice.invoice_number}")
        y -= 0.3 * inch
        p.drawString(1 * inch, y, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")
        y -= 0.3 * inch
        p.drawString(1 * inch, y, f"Due Date: {invoice.due_date}")
        y -= 0.3 * inch
        p.drawString(1 * inch, y, f"Status: {invoice.get_status_display()}")
        y -= 0.5 * inch
        
        # Customer details
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, y, "Bill To:")
        y -= 0.3 * inch
        p.setFont("Helvetica", 12)
        p.drawString(1 * inch, y, f"{invoice.customer.get_full_name() or invoice.customer.username}")
        y -= 0.3 * inch
        if invoice.customer.email:
            p.drawString(1 * inch, y, f"Email: {invoice.customer.email}")
            y -= 0.3 * inch
        if invoice.customer.billing_address:
            p.drawString(1 * inch, y, f"Address: {invoice.customer.billing_address[:50]}")
            y -= 0.3 * inch
        
        # Vendor details (if available)
        if first_line and first_line.product.vendor:
            vendor = first_line.product.vendor
            p.setFont("Helvetica-Bold", 14)
            p.drawString(4.5 * inch, y, "From:")
            y_vendor = y
            y_vendor -= 0.3 * inch
            p.setFont("Helvetica", 12)
            if vendor.company_name:
                p.drawString(4.5 * inch, y_vendor, vendor.company_name)
                y_vendor -= 0.3 * inch
            if vendor.gst_number:
                p.drawString(4.5 * inch, y_vendor, f"GST: {vendor.gst_number}")
                y_vendor -= 0.3 * inch
        
        y -= 0.5 * inch
        
        # Rental details
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, y, "Rental Details:")
        y -= 0.3 * inch
        p.setFont("Helvetica", 12)
        p.drawString(1 * inch, y, f"Order Number: {invoice.rental_order.order_number}")
        y -= 0.5 * inch
        
        # Line items
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y, "Item")
        p.drawString(4 * inch, y, "Qty")
        p.drawString(5 * inch, y, "Rate/Day")
        p.drawString(6 * inch, y, "Days")
        p.drawString(7 * inch, y, "Amount")
        y -= 0.05 * inch
        p.line(1 * inch, y, 7.5 * inch, y)
        y -= 0.3 * inch
        
        p.setFont("Helvetica", 10)
        for line in invoice.rental_order.lines.all():
            p.drawString(1 * inch, y, line.product.name[:30])
            p.drawString(4 * inch, y, str(line.quantity))
            p.drawString(5 * inch, y, f"₹{line.daily_rate}")
            p.drawString(6 * inch, y, str(line.get_duration_days()))
            p.drawString(7 * inch, y, f"₹{line.get_subtotal()}")
            y -= 0.25 * inch
        
        y -= 0.3 * inch
        p.line(1 * inch, y, 7.5 * inch, y)
        y -= 0.3 * inch
        
        # Totals
        p.setFont("Helvetica", 12)
        p.drawString(6 * inch, y, "Subtotal:")
        p.drawString(7 * inch, y, f"₹{invoice.subtotal}")
        y -= 0.25 * inch
        
        p.drawString(6 * inch, y, "Tax:")
        p.drawString(7 * inch, y, f"₹{invoice.tax_amount}")
        y -= 0.25 * inch
        
        if invoice.rental_order.late_fee > 0:
            p.drawString(6 * inch, y, "Late Fee:")
            p.drawString(7 * inch, y, f"₹{invoice.rental_order.late_fee}")
            y -= 0.25 * inch
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(6 * inch, y, "Total:")
        p.drawString(7 * inch, y, f"₹{invoice.total_amount}")
        y -= 0.25 * inch
        
        p.setFont("Helvetica", 12)
        p.drawString(6 * inch, y, "Paid:")
        p.drawString(7 * inch, y, f"₹{invoice.paid_amount}")
        y -= 0.25 * inch
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(6 * inch, y, "Balance:")
        p.drawString(7 * inch, y, f"₹{invoice.get_remaining_balance()}")
        
        # Footer
        p.setFont("Helvetica", 10)
        p.drawString(1 * inch, 1 * inch, "Thank you for your business!")
        
        p.showPage()
        p.save()
        
        return response


# Vendor Views

class VendorInvoicesView(LoginRequiredMixin, ListView):
    """Vendor's invoices (for their products)"""
    model = Invoice
    template_name = 'billing/vendor_invoices.html'
    context_object_name = 'invoices'
    
    def get_queryset(self):
        return Invoice.objects.filter(
            rental_order__lines__product__vendor=self.request.user
        ).distinct().order_by('-created_at')
