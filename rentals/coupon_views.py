"""
Coupon Application Views
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.utils import timezone
from rentals.models import Quotation
from rentals.coupon_models import Coupon


class ApplyCouponView(LoginRequiredMixin, View):
    """Apply coupon to quotation"""
    
    def post(self, request):
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code.')
            return redirect('rentals:view_quotation')
        
        # Get quotation
        try:
            quotation = Quotation.objects.get(customer=request.user, status='DRAFT')
        except Quotation.DoesNotExist:
            messages.error(request, 'No active quotation found.')
            return redirect('rentals:view_quotation')
        
        # Check if already has coupon
        if quotation.applied_coupon:
            messages.warning(request, 'Please remove current coupon before applying a new one.')
            return redirect('rentals:view_quotation')
        
        # Find coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
            return redirect('rentals:view_quotation')
        
        # Validate coupon
        if not coupon.is_valid():
            if not coupon.is_active:
                messages.error(request, 'This coupon is no longer active.')
            elif timezone.now() < coupon.valid_from:
                messages.error(request, 'This coupon is not yet valid.')
            elif timezone.now() > coupon.valid_until:
                messages.error(request, 'This coupon has expired.')
            elif coupon.max_uses > 0 and coupon.uses_count >= coupon.max_uses:
                messages.error(request, 'This coupon has reached its usage limit.')
            else:
                messages.error(request, 'This coupon cannot be used.')
            return redirect('rentals:view_quotation')
        
        # Check if for new users only
        if coupon.for_new_users:
            # Check if user has any previous confirmed quotations/orders
            has_previous_orders = Quotation.objects.filter(
                customer=request.user,
                status='CONFIRMED'
            ).exists()
            
            if has_previous_orders:
                messages.error(request, 'This coupon is only for new users.')
                return redirect('rentals:view_quotation')
        
        # Calculate discount
        order_total = quotation.get_subtotal()
        
        if order_total < coupon.min_order_amount:
            messages.error(
                request,
                f'Minimum order amount of ₹{coupon.min_order_amount} required to use this coupon.'
            )
            return redirect('rentals:view_quotation')
        
        discount = coupon.calculate_discount(order_total)
        
        if discount == 0:
            messages.error(request, 'Coupon cannot be applied to your order.')
            return redirect('rentals:view_quotation')
        
        # Apply coupon
        quotation.applied_coupon = coupon
        quotation.discount_amount = discount
        quotation.save()
        
        messages.success(
            request,
            f'Coupon "{coupon_code}" applied! You saved ₹{discount}.'
        )
        return redirect('rentals:view_quotation')


class RemoveCouponView(LoginRequiredMixin, View):
    """Remove coupon from quotation"""
    
    def post(self, request):
        try:
            quotation = Quotation.objects.get(customer=request.user, status='DRAFT')
            if quotation.applied_coupon:
                coupon_code = quotation.applied_coupon.code
                quotation.applied_coupon = None
                quotation.discount_amount = 0
                quotation.save()
                messages.success(request, f'Coupon "{coupon_code}" removed.')
            else:
                messages.info(request, 'No coupon applied.')
        except Quotation.DoesNotExist:
            messages.error(request, 'No active quotation found.')
        
        return redirect('rentals:view_quotation')
