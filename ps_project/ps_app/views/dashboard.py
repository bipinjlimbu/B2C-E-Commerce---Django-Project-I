from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from ..models import User, Brand, Product, Order, Review

@login_required
def admin_dashboard_view(request):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access the admin dashboard.")
        return redirect('/')
    
    section = request.GET.get('section', 'customer-list')
    
    context = {
        'section' : section,
        'pending_orders_count' : Order.objects.filter(status__in=[Order.Status.PAID, Order.Status.SHIPPING]).count(),
        'awaiting_dispatch_count' : Order.objects.filter(status=Order.Status.PAID).count(),
        'awaiting_delivery_count' : Order.objects.filter(status=Order.Status.SHIPPING).count(),
        'delivered_count' : Order.objects.filter(status=Order.Status.DELIVERED).count(),
        'completed_count' : Order.objects.filter(status=Order.Status.COMPLETED).count(),
        'cancelled_count' : Order.objects.filter(status=Order.Status.CANCELLED).count(),
        'total_gross_revenue' : Order.objects.filter(status=Order.Status.COMPLETED).aggregate(total=models.Sum('total_amount'))['total'] or 0.00
    }
    
    if section == 'customer-list':
        context['customers'] = User.objects.filter(is_staff=False).order_by('-date_joined')
        
    elif section == 'product-management':
        context['products'] = Product.objects.all().order_by('-created_at')
        
    elif section == 'brand-management':
        context['brands'] = Brand.objects.all()

    elif section == 'order-fulfillment':
        context['orders'] = Order.objects.all().order_by('-created_at')
        
    elif section == 'product-reviews':
        context['product_reviews'] = Review.objects.all().order_by('-created_at')
        
    elif section == 'revenue-logs':
        context['revenue_logs'] = Order.objects.filter(status = Order.Status.COMPLETED).order_by('-created_at')
        
    return render(request, 'dashboard/admin_dashboard.html', context)

def customer_dashboard_view(request):
    if not request.user.is_authenticated or request.user.is_staff:
        messages.error(request, "You are not authorized to access the customer dashboard.")
        return redirect('/')
    
    section = request.GET.get('section', 'pending-orders')
    
    context = {
        'section' : section,
        'completed_orders_count' : Order.objects.filter(customer=request.user, status=Order.Status.COMPLETED).count(),
        'cancelled_orders_count' : Order.objects.filter(customer=request.user, status=Order.Status.CANCELLED).count(),
        'gross_spent' : Order.objects.filter(customer=request.user, status=Order.Status.COMPLETED).aggregate(total=models.Sum('total_amount'))['total'] or 0.00,
        'average_spent' : Order.objects.filter(customer=request.user, status=Order.Status.COMPLETED).aggregate(avg=models.Avg('total_amount'))['avg'] or 0.00
    }
        
    if section == 'pending-orders':
        context['pending_orders'] = Order.objects.filter(customer=request.user).exclude(status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED]).order_by('-created_at')
        
    elif section == 'my-orders':
        context['orders'] = Order.objects.filter(customer=request.user, status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED]).order_by('-created_at')
        
    elif section == 'total-spent':
        context['total_spent'] = Order.objects.filter(customer=request.user, status=Order.Status.COMPLETED).order_by('-created_at')
        
    elif section == 'my-reviews':
        context['my_reviews'] = Review.objects.filter(customer=request.user).order_by('-created_at')
        
    return render(request, 'dashboard/customer_dashboard.html', context)