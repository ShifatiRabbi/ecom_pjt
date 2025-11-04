from django.contrib import admin
from .models import Order, OrderItem, IncompleteOrder

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'variant_name', 'unit_price', 'quantity', 'total_price']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 'total_amount', 
                   'order_status', 'payment_status', 'created_at']
    list_filter = ['order_status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
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
            'fields': ('notes', 'ip_address', 'created_at', 'updated_at')
        }),
    )

@admin.register(IncompleteOrder)
class IncompleteOrderAdmin(admin.ModelAdmin):
    list_display = ['customer_phone', 'customer_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer_phone', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']