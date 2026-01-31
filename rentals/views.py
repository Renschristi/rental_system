"""
Rental Management Views
CRITICAL: Implements reservation algorithm to prevent double booking
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Quotation, QuotationLine, RentalOrder, RentalOrderLine
from products.models import Product
from billing.models import Invoice
from django.conf import settings


class AddToQuotationView(LoginRequiredMixin, View):
    """
    Add product to quotation (shopping cart)
    Validates dates and calculates price
    """
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_published=True)
        
        # Get form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid date format.')
            return redirect('products:product_detail', pk=product_id)
        
        # Validate date range
        if start_date < timezone.now().date():
            messages.error(request, 'Start date cannot be in the past.')
            return redirect('products:product_detail', pk=product_id)
        
        if end_date <= start_date:
            messages.error(request, 'End date must be after start date.')
            return redirect('products:product_detail', pk=product_id)
        
        # Validate quantity
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('products:product_detail', pk=product_id)
        
        # Check preliminary availability (not strict, just a warning)
        if not product.is_available(start_date, end_date, quantity):
            messages.warning(request, 'Limited availability for selected dates. Please confirm soon.')
        
        # Get or create draft quotation
        quotation, created = Quotation.objects.get_or_create(
            customer=request.user,
            status='DRAFT'
        )
        
        # Check if product already in quotation
        quotation_line, line_created = QuotationLine.objects.get_or_create(
            quotation=quotation,
            product=product,
            defaults={
                'quantity': quantity,
                'start_date': start_date,
                'end_date': end_date,
                'daily_rate': product.daily_rate
            }
        )
        
        if not line_created:
            # Update existing line
            quotation_line.quantity = quantity
            quotation_line.start_date = start_date
            quotation_line.end_date = end_date
            quotation_line.daily_rate = product.daily_rate
            quotation_line.save()
        
        messages.success(request, f'{product.name} added to quotation!')
        return redirect('rentals:view_quotation')


class ViewQuotationView(LoginRequiredMixin, View):
    """
    View current quotation (cart)
    Allows editing before confirmation
    """
    
    def get(self, request):
        try:
            quotation = Quotation.objects.get(customer=request.user, status='DRAFT')
            lines = quotation.lines.select_related('product').all()
        except Quotation.DoesNotExist:
            quotation = None
            lines = []
        
        context = {
            'quotation': quotation,
            'lines': lines,
        }
        return render(request, 'rentals/quotation.html', context)


class RemoveFromQuotationView(LoginRequiredMixin, View):
    """Remove item from quotation"""
    
    def post(self, request, line_id):
        quotation = get_object_or_404(Quotation, customer=request.user, status='DRAFT')
        line = get_object_or_404(QuotationLine, id=line_id, quotation=quotation)
        
        product_name = line.product.name
        line.delete()
        
        messages.success(request, f'{product_name} removed from quotation.')
        return redirect('rentals:view_quotation')


class ConfirmQuotationView(LoginRequiredMixin, View):
    """
    CRITICAL: Confirm quotation and create rental order
    Implements reservation algorithm to prevent double booking
    Uses database transaction for atomicity
    """
    
    @transaction.atomic
    def post(self, request):
        # Get quotation with SELECT FOR UPDATE to prevent race conditions
        try:
            quotation = Quotation.objects.select_for_update().get(
                customer=request.user,
                status='DRAFT'
            )
        except Quotation.DoesNotExist:
            messages.error(request, 'No quotation found.')
            return redirect('rentals:view_quotation')
        
        if not quotation.lines.exists():
            messages.error(request, 'Quotation is empty.')
            return redirect('rentals:view_quotation')
        
        # STEP 1: Validate availability for ALL items
        # This is the reservation algorithm - check for overlapping bookings
        unavailable_items = []
        
        for line in quotation.lines.select_related('product').all():
            # Lock product row to prevent concurrent reservations
            product = Product.objects.select_for_update().get(id=line.product.id)
            
            # Check availability for this specific date range
            available_qty = product.get_available_quantity(line.start_date, line.end_date)
            
            if available_qty < line.quantity:
                unavailable_items.append({
                    'product': product.name,
                    'requested': line.quantity,
                    'available': available_qty,
                    'dates': f"{line.start_date} to {line.end_date}"
                })
        
        # If any item is unavailable, abort entire transaction
        if unavailable_items:
            error_msg = "Unable to confirm order. The following items are no longer available:\n"
            for item in unavailable_items:
                error_msg += f"- {item['product']}: Requested {item['requested']}, Available {item['available']} ({item['dates']})\n"
            messages.error(request, error_msg)
            return redirect('rentals:view_quotation')
        
        # STEP 2: Create Rental Order
        # Generate unique order number
        order_number = f"RO-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
        
        rental_order = RentalOrder.objects.create(
            customer=request.user,
            quotation=quotation,
            order_number=order_number,
            status='CONFIRMED'
        )
        
        # STEP 3: Create Rental Order Lines (This locks the inventory)
        for quotation_line in quotation.lines.all():
            RentalOrderLine.objects.create(
                rental_order=rental_order,
                product=quotation_line.product,
                quantity=quotation_line.quantity,
                start_date=quotation_line.start_date,
                end_date=quotation_line.end_date,
                daily_rate=quotation_line.daily_rate
            )
        
        # STEP 4: Mark quotation as confirmed
        quotation.status = 'CONFIRMED'
        quotation.confirmed_at = timezone.now()
        quotation.save()
        
        # STEP 5: Create Invoice
        self._create_invoice(rental_order)
        
        messages.success(request, f'Rental order {order_number} confirmed successfully!')
        return redirect('rentals:rental_detail', pk=rental_order.id)
    
    def _create_invoice(self, rental_order):
        """Create invoice for rental order"""
        # Calculate amounts
        subtotal = rental_order.get_total()
        tax_rate = Decimal(str(settings.TAX_RATE))
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Generate invoice number
        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}-{rental_order.customer.id}"
        
        # Due date: 7 days from now
        due_date = timezone.now().date() + timedelta(days=7)
        
        Invoice.objects.create(
            rental_order=rental_order,
            customer=rental_order.customer,
            invoice_number=invoice_number,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            due_date=due_date,
            status='DRAFT'
        )


class MyRentalsView(LoginRequiredMixin, ListView):
    """Customer's rental orders"""
    model = RentalOrder
    template_name = 'rentals/my_rentals.html'
    context_object_name = 'rentals'
    
    def get_queryset(self):
        return RentalOrder.objects.filter(customer=self.request.user).order_by('-created_at')


class RentalDetailView(LoginRequiredMixin, DetailView):
    """Rental order detail"""
    model = RentalOrder
    template_name = 'rentals/rental_detail.html'
    context_object_name = 'rental'
    
    def get_queryset(self):
        # Customers can only view their own rentals
        if self.request.user.is_customer():
            return RentalOrder.objects.filter(customer=self.request.user)
        # Vendors can view rentals for their products
        elif self.request.user.is_vendor():
            return RentalOrder.objects.filter(lines__product__vendor=self.request.user).distinct()
        # Admins can view all
        return RentalOrder.objects.all()


# Vendor Views

class VendorRentalListView(LoginRequiredMixin, ListView):
    """Vendor's rental orders (for products they own)"""
    model = RentalOrder
    template_name = 'rentals/vendor_rentals.html'
    context_object_name = 'rentals'
    
    def get_queryset(self):
        # Get rentals that contain vendor's products
        queryset = RentalOrder.objects.filter(
            lines__product__vendor=self.request.user
        ).distinct().order_by('-created_at')
        
        # Filter options from diagram
        filter_type = self.request.GET.get('filter', '')
        
        # Filter: Invoiced and Paid orders only
        if filter_type == 'paid':
            queryset = queryset.filter(
                invoices__status='PAID'
            ).distinct()
        
        # Filter: Approaching or past return dates
        elif filter_type == 'returning':
            from datetime import timedelta
            today = timezone.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Orders where return date is within 1 day or already passed
            queryset = queryset.filter(
                status='ACTIVE',
                lines__end_date__lte=tomorrow
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get('filter', '')
        return context


class PickupRentalView(LoginRequiredMixin, View):
    """
    Mark rental as picked up (CONFIRMED -> ACTIVE)
    Vendor action
    """
    
    def post(self, request, pk):
        rental = get_object_or_404(
            RentalOrder,
            pk=pk,
            lines__product__vendor=request.user,
            status='CONFIRMED'
        )
        
        rental.mark_as_active()
        messages.success(request, f'Rental {rental.order_number} marked as picked up.')
        return redirect('rentals:vendor_rentals')


class ReturnRentalView(LoginRequiredMixin, View):
    """
    Process rental return (ACTIVE -> RETURNED)
    Calculates late fees if applicable
    Vendor action
    """
    
    @transaction.atomic
    def post(self, request, pk):
        rental = get_object_or_404(
            RentalOrder,
            pk=pk,
            lines__product__vendor=request.user,
            status='ACTIVE'
        )
        
        # Mark as returned (this calculates late fees automatically)
        rental.mark_as_returned()
        
        # Update invoice if late fees were added
        if rental.late_fee > 0:
            invoice = rental.invoices.first()
            if invoice:
                invoice.subtotal += rental.late_fee
                invoice.total_amount = invoice.subtotal + invoice.tax_amount
                invoice.save()
            
            messages.warning(
                request,
                f'Rental returned with late fee: ${rental.late_fee}. Invoice updated.'
            )
        else:
            messages.success(request, f'Rental {rental.order_number} returned successfully.')
        
        return redirect('rentals:vendor_rentals')
