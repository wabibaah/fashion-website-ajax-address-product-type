from . models import Cart, CartItem
from . views import _cart_id


def counter(request):
  cart_count = 0
  if 'admin' in request.path:
    return {}
  
  else:
    try:
      cart = Cart.objects.filter(cart_id=_cart_id(request))
      if request.user.is_authenticated:
        cart_items = CartItem.objects.all().filter(user=request.user)
      else:
        cart_items = CartItem.objects.all().filter(cart=cart[:1])
      
      for cart_item in cart_items:
        cart_count = cart_count + cart_item.quantity
    except Cart.DoesNotExist:
      cart_cout = 0

  return dict(cart_count=cart_count)




### in this context processor, we are getting all the imports easily from cart and cart items in the model but we can use dictionaries here anytime at all we want
## we must go to the settings and carts.context_processors.counter