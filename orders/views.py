import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, IncompleteOrder
from cart.models import Cart, CartItem

def checkout(request):
    cart = get_or_create_cart(request)
    if cart.get_total_quantity() == 0:
        return redirect('cart:cart_detail')
    
    return render(request, 'orders/checkout.html', {'cart': cart})

@require_POST
@csrf_exempt
def create_order(request):
    try:
        data = json.loads(request.body)
        cart = get_or_create_cart(request)
        
        if cart.get_total_quantity() == 0:
            return JsonResponse({
                'success': False,
                'message': 'Cart is empty'
            })
        
        # Create order
        order = Order(
            session_key=request.session.session_key,
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data['customer_phone'],
            shipping_address=data['shipping_address'],
            shipping_city=data['shipping_city'],
            shipping_state=data['shipping_state'],
            shipping_zip_code=data['shipping_zip_code'],
            shipping_country=data['shipping_country'],
            subtotal=cart.get_total_price(),
            total_amount=cart.get_total_price(),
            payment_method=data['payment_method'],
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
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': f'/orders/thank-you/{order.order_number}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def thank_you(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/thank_you.html', {'order': order})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart