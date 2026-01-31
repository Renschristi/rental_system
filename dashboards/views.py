"""
Dashboard and Analytics Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from products.models import Product
from rentals.models import RentalOrder
from billing.models import Invoice, Payment
from accounts.models import User


@login_required
def home_view(request):
    """
    Home dashboard - shows different views based on user role
    """
    user = request.user
    
    if user.is_customer():
        return customer_dashboard(request)
    elif user.is_vendor():
        return vendor_dashboard(request)
    elif user.is_admin():
        return admin_dashboard(request)
    else:
        return customer_dashboard(request)


def customer_dashboard(request):
    """Customer dashboard"""
    # Active rentals
    active_rentals = RentalOrder.objects.filter(
        customer=request.user,
        status__in=['CONFIRMED', 'ACTIVE']
    ).count()
    
    # Past rentals
    past_rentals = RentalOrder.objects.filter(
        customer=request.user,
        status='RETURNED'
    ).count()
    
    # Pending invoices
    pending_invoices = Invoice.objects.filter(
        customer=request.user,
        status__in=['DRAFT', 'PARTIAL']
    ).count()
    
    # Recent rentals
    recent_rentals = RentalOrder.objects.filter(
        customer=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'dashboard_type': 'customer',
        'active_rentals': active_rentals,
        'past_rentals': past_rentals,
        'pending_invoices': pending_invoices,
        'recent_rentals': recent_rentals,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


def vendor_dashboard(request):
    """Vendor dashboard"""
    # Active rentals (for vendor's products)
    active_rentals = RentalOrder.objects.filter(
        lines__product__vendor=request.user,
        status='ACTIVE'
    ).distinct().count()
    
    # Upcoming pickups
    upcoming_pickups = RentalOrder.objects.filter(
        lines__product__vendor=request.user,
        status='CONFIRMED'
    ).distinct().count()
    
    # Pending returns
    pending_returns = RentalOrder.objects.filter(
        lines__product__vendor=request.user,
        status='ACTIVE'
    ).distinct().count()
    
    # Total earnings (from paid invoices)
    total_earnings = Invoice.objects.filter(
        rental_order__lines__product__vendor=request.user,
        status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Recent rentals
    recent_rentals = RentalOrder.objects.filter(
        lines__product__vendor=request.user
    ).distinct().order_by('-created_at')[:10]
    
    # Product count
    product_count = Product.objects.filter(vendor=request.user).count()
    
    context = {
        'dashboard_type': 'vendor',
        'active_rentals': active_rentals,
        'upcoming_pickups': upcoming_pickups,
        'pending_returns': pending_returns,
        'total_earnings': total_earnings,
        'recent_rentals': recent_rentals,
        'product_count': product_count,
    }
    return render(request, 'dashboards/vendor_dashboard.html', context)


def admin_dashboard(request):
    """Admin dashboard with system-wide analytics"""
    # Total revenue
    total_revenue = Invoice.objects.filter(
        status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Active rentals
    active_rentals = RentalOrder.objects.filter(
        status__in=['CONFIRMED', 'ACTIVE']
    ).count()
    
    # Total customers
    total_customers = User.objects.filter(role='CUSTOMER').count()
    
    # Total vendors
    total_vendors = User.objects.filter(role='VENDOR').count()
    
    # Most rented products (top 5)
    most_rented = Product.objects.annotate(
        rental_count=Count('rentalorderline')
    ).order_by('-rental_count')[:5]
    
    # Revenue by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_revenue = Invoice.objects.filter(
        created_at__gte=six_months_ago,
        status='PAID'
    ).extra(select={
        'month': 'EXTRACT(month FROM created_at)',
        'year': 'EXTRACT(year FROM created_at)'
    }).values('year', 'month').annotate(
        revenue=Sum('total_amount')
    ).order_by('year', 'month')
    
    # Recent orders
    recent_orders = RentalOrder.objects.all().order_by('-created_at')[:10]
    
    # Pending payments
    pending_payment_amount = Invoice.objects.filter(
        status__in=['DRAFT', 'PARTIAL']
    ).aggregate(
        total=Sum(F('total_amount') - F('paid_amount'))
    )['total'] or Decimal('0')
    
    context = {
        'dashboard_type': 'admin',
        'total_revenue': total_revenue,
        'active_rentals': active_rentals,
        'total_customers': total_customers,
        'total_vendors': total_vendors,
        'most_rented': most_rented,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'pending_payment_amount': pending_payment_amount,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def analytics_view(request):
    """
    Detailed analytics page
    Admin only
    """
    if not request.user.is_admin():
        return render(request, 'dashboards/403.html', status=403)
    
    # Date range filtering
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Rental statistics
    rentals_in_period = RentalOrder.objects.filter(created_at__gte=start_date)
    
    total_rentals = rentals_in_period.count()
    confirmed_rentals = rentals_in_period.filter(status='CONFIRMED').count()
    active_rentals = rentals_in_period.filter(status='ACTIVE').count()
    returned_rentals = rentals_in_period.filter(status='RETURNED').count()
    
    # Revenue statistics
    invoices_in_period = Invoice.objects.filter(created_at__gte=start_date)
    
    total_invoiced = invoices_in_period.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    total_paid = invoices_in_period.filter(status='PAID').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Product utilization
    product_stats = Product.objects.annotate(
        total_rentals=Count('rentalorderline'),
        total_revenue=Sum('rentalorderline__daily_rate')
    ).order_by('-total_rentals')[:10]
    
    context = {
        'days': days,
        'total_rentals': total_rentals,
        'confirmed_rentals': confirmed_rentals,
        'active_rentals': active_rentals,
        'returned_rentals': returned_rentals,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'product_stats': product_stats,
    }
    return render(request, 'dashboards/analytics.html', context)
