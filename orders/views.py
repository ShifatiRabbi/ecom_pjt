import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
import logging
from .models import Order, OrderItem, IncompleteOrder
from cart.models import Cart, CartItem

logger = logging.getLogger(__name__)

def get_or_create_cart(request):
    """Get or create cart for the current session"""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def checkout(request):
    """Checkout page view"""
    cart = get_or_create_cart(request)
    if cart.get_total_quantity() == 0:
        return redirect('cart:cart_detail')
    
    # Check if there's an incomplete order for this session
    incomplete_order = None
    if request.session.session_key:
        try:
            incomplete_order = IncompleteOrder.objects.get(session_key=request.session.session_key)
        except IncompleteOrder.DoesNotExist:
            pass
    
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'incomplete_order': incomplete_order
    })

@require_POST
@csrf_exempt
def save_incomplete_order(request):
    """Save incomplete order when user enters phone number"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('customer_phone', '').strip()
        email = data.get('customer_email', '').strip()
        
        if not phone_number:
            return JsonResponse({
                'success': False,
                'message': 'Phone number is required'
            })
        
        cart = get_or_create_cart(request)
        
        if cart.get_total_quantity() == 0:
            return JsonResponse({
                'success': False,
                'message': 'Cart is empty'
            })
        
        # Prepare cart data for saving
        cart_data = {
            'items': [],
            'total_quantity': cart.get_total_quantity(),
            'total_price': str(cart.get_total_price())
        }
        
        for item in cart.items.all():
            cart_data['items'].append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'variant_id': item.variant.id if item.variant else None,
                'variant_name': item.variant.variant_name if item.variant else '',
                'quantity': item.quantity,
                'unit_price': str(item.get_unit_price()),
                'total_price': str(item.get_total_price())
            })
        
        # Save or update incomplete order
        incomplete_order, created = IncompleteOrder.objects.update_or_create(
            session_key=request.session.session_key,
            defaults={
                'customer_phone': phone_number,
                'customer_email': email,
                'cart_data': cart_data
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Progress saved',
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error saving incomplete order: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error saving progress'
        })

@require_POST
@csrf_exempt
def create_order(request):
    """Create final order from checkout"""
    try:
        data = json.loads(request.body)
        cart = get_or_create_cart(request)
        
        if cart.get_total_quantity() == 0:
            return JsonResponse({
                'success': False,
                'message': 'Cart is empty'
            })
        
        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'customer_phone', 
                          'shipping_address', 'shipping_city', 'shipping_state', 
                          'shipping_zip_code', 'shipping_country', 'payment_method']
        
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                })
        
        # Use transaction to ensure data consistency
        with transaction.atomic():
            # Create order
            order = Order(
                session_key=request.session.session_key,
                customer_name=data['customer_name'].strip(),
                customer_email=data['customer_email'].strip(),
                customer_phone=data['customer_phone'].strip(),
                shipping_address=data['shipping_address'].strip(),
                shipping_city=data['shipping_city'].strip(),
                shipping_state=data['shipping_state'].strip(),
                shipping_zip_code=data['shipping_zip_code'].strip(),
                shipping_country=data['shipping_country'].strip(),
                subtotal=cart.get_total_price(),
                total_amount=cart.get_total_price(),
                payment_method=data['payment_method'],
                notes=data.get('notes', '').strip(),
                ip_address=get_client_ip(request)
            )
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    product_name=cart_item.product.name,
                    variant_name=cart_item.variant.variant_name if cart_item.variant else '',
                    unit_price=cart_item.get_unit_price(),
                    quantity=cart_item.quantity,
                    total_price=cart_item.get_total_price()
                )
            
            # Clear cart
            cart.items.all().delete()
            
            # Delete incomplete order if exists
            try:
                incomplete_order = IncompleteOrder.objects.get(session_key=request.session.session_key)
                incomplete_order.delete()
                logger.info(f"Deleted incomplete order for session {request.session.session_key}")
            except IncompleteOrder.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': f'/orders/thank-you/{order.order_number}/'
        })
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error creating order. Please try again.'
        })

def thank_you(request, order_number):
    """Thank you page after successful order"""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/thank_you.html', {'order': order})

