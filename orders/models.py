# from django.db import models
# from products.models import Product, ProductVariant

# ORDER_STATUS = (
#     ('pending', 'Pending'),
#     ('confirmed', 'Confirmed'),
#     ('processing', 'Processing'),
#     ('shipped', 'Shipped'),
#     ('delivered', 'Delivered'),
#     ('cancelled', 'Cancelled'),
#     ('refunded', 'Refunded'),
# )

# PAYMENT_STATUS = (
#     ('pending', 'Pending'),
#     ('paid', 'Paid'),
#     ('failed', 'Failed'),
#     ('refunded', 'Refunded'),
# )

# PAYMENT_METHODS = (
#     ('credit_card', 'Credit Card'),
#     ('debit_card', 'Debit Card'),
#     ('paypal', 'PayPal'),
#     ('bank_transfer', 'Bank Transfer'),
#     ('cash_on_delivery', 'Cash on Delivery'),
# )

# class Order(models.Model):
#     order_number = models.CharField(max_length=20, unique=True)
#     session_key = models.CharField(max_length=40)
    
#     # Customer information
#     customer_name = models.CharField(max_length=100)
#     customer_email = models.EmailField()
#     customer_phone = models.CharField(max_length=20)
    
#     # Shipping address
#     shipping_address = models.TextField()
#     shipping_city = models.CharField(max_length=100)
#     shipping_state = models.CharField(max_length=100)
#     shipping_zip_code = models.CharField(max_length=20)
#     shipping_country = models.CharField(max_length=100)
    
#     # Billing address (same as shipping by default)
#     billing_address = models.TextField(blank=True)
#     billing_city = models.CharField(max_length=100, blank=True)
#     billing_state = models.CharField(max_length=100, blank=True)
#     billing_zip_code = models.CharField(max_length=20, blank=True)
#     billing_country = models.CharField(max_length=100, blank=True)
    
#     # Order details
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)
#     tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
#     # Status
#     order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     paid_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
    
#     # Additional fields
#     notes = models.TextField(blank=True)
#     ip_address = models.GenericIPAddressField(blank=True, null=True)
    
#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.order_number
    
#     def save(self, *args, **kwargs):
#         if not self.order_number:
#             import random
#             import string
#             self.order_number = 'ORD' + ''.join(random.choices(string.digits, k=10))
        
#         if not self.billing_address:
#             self.billing_address = self.shipping_address
#             self.billing_city = self.shipping_city
#             self.billing_state = self.shipping_state
#             self.billing_zip_code = self.shipping_zip_code
#             self.billing_country = self.shipping_country
        
#         super().save(*args, **kwargs)

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
#     product_name = models.CharField(max_length=200)
#     variant_name = models.CharField(max_length=100, blank=True)
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
#     def __str__(self):
#         return f"{self.product_name} - {self.order.order_number}"

# class IncompleteOrder(models.Model):
#     session_key = models.CharField(max_length=40)
#     customer_phone = models.CharField(max_length=20)
#     customer_email = models.EmailField(blank=True)
#     cart_data = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"Incomplete Order - {self.customer_phone}"
    
#     def get_cart_summary(self):
#         """Get a summary of cart items for display"""
#         if self.cart_data and 'items' in self.cart_data:
#             items = self.cart_data['items']
#             return f"{len(items)} item(s) - ${self.cart_data.get('total_price', '0.00')}"
#         return "Empty cart"
    
#     def get_items_list(self):
#         """Get list of items for admin display"""
#         if self.cart_data and 'items' in self.cart_data:
#             return [
#                 f"{item.get('product_name', 'Unknown')} (Qty: {item.get('quantity', 0)})"
#                 for item in self.cart_data['items']
#             ]
#         return []



from django.db import models
from products.models import Product, ProductVariant
import uuid
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib

ORDER_STATUS = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
)

PAYMENT_STATUS = (
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
)

PAYMENT_METHODS = (
    ('cash_on_delivery', 'Cash on Delivery'),
)

DELIVERY_AREAS = (
    ('inside_dhaka', 'ঢাকা সিটির ভেতরে'),
    ('outside_dhaka', 'ঢাকা সিটির বাইরে'),
)

class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    session_key = models.CharField(max_length=40)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20)
    
    # Shipping address
    delivery_area = models.CharField(max_length=20, choices=DELIVERY_AREAS, default='inside_dhaka')
    shipping_address = models.TextField()
    notes = models.TextField(blank=True)
    
    # Location data
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    detected_city = models.CharField(max_length=100, blank=True)
    detected_region = models.CharField(max_length=100, blank=True)
    detected_country = models.CharField(max_length=100, blank=True)
    
    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash_on_delivery')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_number
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'ORD' + ''.join(random.choices(string.digits, k=10))
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    variant_name = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_name} - {self.order.order_number}"

class IncompleteOrder(models.Model):
    session_key = models.CharField(max_length=40)
    customer_phone = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField(blank=True)
    delivery_area = models.CharField(max_length=20, choices=DELIVERY_AREAS, default='inside_dhaka')
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Location data
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    detected_city = models.CharField(max_length=100, blank=True)
    detected_region = models.CharField(max_length=100, blank=True)
    detected_country = models.CharField(max_length=100, blank=True)
    
    # Cart data (encrypted)
    encrypted_cart_data = models.TextField(blank=True)
    cart_hash = models.CharField(max_length=64, blank=True)  # For verification
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Incomplete Order - {self.customer_phone}"
    
    def set_cart_data(self, cart_data):
        """Encrypt and store cart data"""
        # Generate hash for verification
        cart_json = json.dumps(cart_data, sort_keys=True, cls=DjangoJSONEncoder)
        self.cart_hash = hashlib.sha256(cart_json.encode()).hexdigest()
        
        # Encrypt the data
        cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        self.encrypted_cart_data = cipher_suite.encrypt(cart_json.encode()).decode()
    
    def get_cart_data(self):
        """Decrypt and return cart data"""
        if not self.encrypted_cart_data:
            return None
        
        try:
            cipher_suite = Fernet(settings.ENCRYPTION_KEY)
            decrypted_data = cipher_suite.decrypt(self.encrypted_cart_data.encode()).decode()
            
            # Verify hash
            if hashlib.sha256(decrypted_data.encode()).hexdigest() != self.cart_hash:
                return None
                
            return json.loads(decrypted_data)
        except Exception:
            return None
    
    def get_cart_summary(self):
        """Get a summary of cart items for display"""
        cart_data = self.get_cart_data()
        if cart_data and 'items' in cart_data:
            items = cart_data['items']
            return f"{len(items)} item(s) - ৳{cart_data.get('total_price', '0.00')}"
        return "Empty cart"

