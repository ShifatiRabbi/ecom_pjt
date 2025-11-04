from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem, IncompleteOrder
from ecommerce_project.admin_site import custom_admin_site

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'variant_name', 'unit_price', 'quantity', 'total_price']
    extra = 0
    can_delete = False
    classes = ['collapse']

    def has_add_permission(self, request, obj):
        return False

@admin.register(Order, site=custom_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_info', 'total_amount', 
                   'order_status_badge', 'payment_status_badge', 'created_at', 'view_order_link']
    list_filter = ['order_status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_per_page = 20
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'session_key', 'order_status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_zip_code', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state',
                      'billing_zip_code', 'billing_country')
        }),
        ('Order Amounts', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 
                      'discount_amount', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'paid_at', 'completed_at')
        }),
        ('Additional Information', {
            'fields': ('notes', 'ip_address', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>{}<br>{}',
            obj.customer_name,
            obj.customer_email,
            obj.customer_phone
        )
    customer_info.short_description = 'Customer'

    def order_status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'success',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary'
        }
        color = status_colors.get(obj.order_status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_order_status_display()
        )
    order_status_badge.short_description = 'Status'

    def payment_status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'paid': 'success',
            'failed': 'danger',
            'refunded': 'info'
        }
        color = status_colors.get(obj.payment_status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'

    def view_order_link(self, obj):
        edit_url = reverse('custom_admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}" class="button">View/Edit</a>', edit_url)
    view_order_link.short_description = 'Actions'

    def changelist_view(self, request, extra_context=None):
        # Add custom filters to the context
        extra_context = extra_context or {}
        extra_context['pending_count'] = Order.objects.filter(order_status='pending').count()
        extra_context['processing_count'] = Order.objects.filter(order_status='processing').count()
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(IncompleteOrder, site=custom_admin_site)
class IncompleteOrderAdmin(admin.ModelAdmin):
    list_display = ['customer_phone', 'customer_email', 'cart_items_count', 'created_at', 'contact_actions']
    list_filter = ['created_at']
    search_fields = ['customer_phone', 'customer_email']
    readonly_fields = ['created_at', 'updated_at', 'cart_data_preview']
    list_per_page = 20

    def cart_items_count(self, obj):
        if obj.cart_data and 'items' in obj.cart_data:
            return len(obj.cart_data['items'])
        return 0
    cart_items_count.short_description = 'Items'

    def cart_data_preview(self, obj):
        if obj.cart_data:
            items = obj.cart_data.get('items', [])
            preview = []
            for item in items:
                preview.append(f"• {item.get('product_name', 'Unknown')} - Qty: {item.get('quantity', 0)}")
            return format_html('<br>'.join(preview))
        return "No cart data"
    cart_data_preview.short_description = 'Cart Items'

    def contact_actions(self, obj):
        call_url = f"tel:{obj.customer_phone}"
        sms_url = f"sms:{obj.customer_phone}"
        email_url = f"mailto:{obj.customer_email}" if obj.customer_email else "#"
        
        return format_html(
            '<a href="{}" class="button" title="Call">📞</a> '
            '<a href="{}" class="button" title="SMS">💬</a> '
            '{}',
            call_url,
            sms_url,
            format_html('<a href="{}" class="button" title="Email">📧</a>', email_url) if obj.customer_email else ''
        )
    contact_actions.short_description = 'Contact'