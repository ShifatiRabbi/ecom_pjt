import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, CartItem
from products.models import Product, ProductVariant

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
@csrf_exempt
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))
        buy_now = data.get('buy_now', False)
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        if buy_now:
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('orders:checkout'),
                'cart_total_quantity': cart.get_total_quantity()
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart',
                'cart_total_quantity': cart.get_total_quantity()
            })
        
        # return JsonResponse({
        #     'success': True,
        #     'message': 'Product added to cart',
        #     'cart_total_quantity': cart.get_total_quantity()
        # })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=request.session.session_key)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = get_or_create_cart(request)
        
        return JsonResponse({
            'success': True,
            'cart_total_quantity': cart.get_total_quantity(),
            'item_total_price': cart_item.get_total_price(),
            'cart_total_price': cart.get_total_price()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__session_key=request.session.session_key)
        cart_item.delete()
        
        cart = get_or_create_cart(request)
        
        return JsonResponse({
            'success': True,
            'cart_total_quantity': cart.get_total_quantity(),
            'cart_total_price': cart.get_total_price()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })