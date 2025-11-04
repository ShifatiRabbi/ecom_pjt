from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from orders.models import Order, IncompleteOrder

class CustomAdminSite(admin.AdminSite):
    site_header = "ShopNow Administration"
    site_title = "ShopNow Admin Portal"
    index_title = "Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard), name='dashboard'),
        ]
        return custom_urls + urls
    
    @login_required
    def dashboard(self, request):
        # Calculate time ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Order statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(order_status='pending').count()
        completed_orders = Order.objects.filter(order_status='delivered').count()
        
        # Recent orders (last 7 days)
        recent_orders = Order.objects.filter(created_at__gte=week_ago).count()
        
        # Revenue calculations
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        monthly_revenue = Order.objects.filter(
            payment_status='paid',
            created_at__gte=month_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Product statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=5, 
            stock_quantity__gt=0
        ).count()
        out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
        
        # Customer statistics
        incomplete_orders = IncompleteOrder.objects.count()
        
        # Recent orders for display
        recent_orders_list = Order.objects.all().order_by('-created_at')[:10]
        
        # Top selling products
        top_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:5]
        
        # Sales chart data (last 7 days)
        sales_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_sales = Order.objects.filter(
                created_at__date=date,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            sales_data.append({
                'date': date.strftime('%b %d'),
                'sales': float(day_sales)
            })
        sales_data.reverse()
        
        context = {
            **self.each_context(request),
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'recent_orders': recent_orders,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'incomplete_orders': incomplete_orders,
            'recent_orders_list': recent_orders_list,
            'top_products': top_products,
            'sales_data': sales_data,
        }
        
        return render(request, 'admin/dashboard.html', context)

# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with custom admin site
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)