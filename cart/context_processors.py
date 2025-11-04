from .models import Cart

def cart_total_amount(request):
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            return {
                'cart_total_quantity': cart.get_total_quantity(),
                'cart_total_price': cart.get_total_price()
            }
        except Cart.DoesNotExist:
            pass
    return {
        'cart_total_quantity': 0,
        'cart_total_price': 0
    }