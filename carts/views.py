from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from . models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  
  return cart


def add_cart(request, product_id):
  current_user = request.user
  product = Product.objects.get(id=product_id)
  ### if the user is authenticated
  if current_user.is_authenticated:
    product_variation = []
    if request.method == 'POST':
      # color = request.POST['color']
      # size  = request.POST['size']
      for item in request.POST:
        key = item
        value = request.POST[key]
        # print(key, value) 
      ## checking if the key and value pairs much exactly with the one in the model even though we did a dropdown we don't want to trust them
        try:
          variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
          product_variation.append(variation)
        except:
          pass


    ### if the user is logged in we don't need the cart id (but) we need the user which is the same as the current_user


    is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
    if is_cart_item_exists:
      cart_item = CartItem.objects.filter(product=product, user=current_user)

      ex_var_list = []
      id = []
      for item in cart_item:
        existing_variation = item.variations.all()
        ex_var_list.append(list(existing_variation))
        id.append(item.id)

      if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item_id = id[index]
        item = CartItem.objects.get(product=product, id=item_id)
        item.quantity += 1
        item.save()
        
      else:
        item = CartItem.objects.create(product=product, quantity=1, user=current_user)
        if len(product_variation) > 0:
          item.variations.clear()
          item.variations.add(*product_variation)
        item.save()


    else:
      cart_item = CartItem.objects.create(
        product = product,
        quantity = 1,
        user = current_user,
      )
      if len(product_variation) > 0:
        cart_item.variations.clear()
        cart_item.variations.add(*product_variation)
      cart_item.save()

    return redirect('cart')
  ### if the user is not authenticated
  else:
    product_variation = []
    if request.method == 'POST':
      # color = request.POST['color']
      # size  = request.POST['size']
      for item in request.POST:
        key = item
        value = request.POST[key]
        # print(key, value) 
      ## checking if the key and value pairs much exactly with the one in the model even though we did a dropdown we don't want to trust them
        try:
          variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
          product_variation.append(variation)
        except:
          pass


    try:
      cart = Cart.objects.get(cart_id=_cart_id(request))
    
    except Cart.DoesNotExist:
      cart = Cart.objects.create(
        cart_id = _cart_id(request)
      )
    cart.save()  ### this cart saving is for both the try and the exception


    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
      cart_item = CartItem.objects.filter(product=product, cart=cart)

      ex_var_list = []
      id = []
      for item in cart_item:
        existing_variation = item.variations.all()
        ex_var_list.append(list(existing_variation))
        id.append(item.id)
      print(ex_var_list)

      if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item_id = id[index]
        item = CartItem.objects.get(product=product, id=item_id)
        item.quantity += 1
        item.save()
        
      else:
        item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
          item.variations.clear()
          item.variations.add(*product_variation)
        item.save()


    else:
      cart_item = CartItem.objects.create(
        product = product,
        quantity = 1,
        cart = cart,
      )
      if len(product_variation) > 0:
        cart_item.variations.clear()
        cart_item.variations.add(*product_variation)
      cart_item.save()

    return redirect('cart')


## reduce the number on the cart items by 1 (one)
def remove_cart(request, product_id, cart_item_id):
  
  product = get_object_or_404(Product, id=product_id)

  try:
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    if cart_item.quantity > 1:
      cart_item.quantity -= 1
      cart_item.save()
    else:
      cart_item.delete()
  
  except:
    pass
  
  return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
  product = get_object_or_404(Product, id=product_id)
  if request.user.is_authenticated:
    cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
  else:  
    cart = Cart.objects.get(cart_id=_cart_id(request))  
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
  cart_item.delete()
  return redirect('cart')

 

def cart(request, total=0, quantity=0, cart_items=None):
  try:
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for cart_item in cart_items:
      total += (cart_item.product.price * cart_item.quantity)
      quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax
  
  except ObjectDoesNotExist:
    ## Just ignore
    pass 

  context = {
    'total': total,
    'quantity': quantity,
    'cart_items': cart_items,
    'tax': tax,
    'grand_total': grand_total
  }
  return render(request, 'store/cart.html', context)


@login_required(login_url = 'login') 
def checkout(request, total=0, quantity=0, cart_items=None):
  try:
    tax = 0
    grand_total = 0
    # cart = Cart.objects.get(cart_id=_cart_id(request))
    # cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    # else:
    #   cart = Cart.objects.get(cart_id=_cart_id(request))
    #   cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for cart_item in cart_items:
      total += (cart_item.product.price * cart_item.quantity)
      quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax
  
  except ObjectDoesNotExist:
    ## Just ignore
    pass 

  context = {
    'total': total,
    'quantity': quantity,
    'cart_items': cart_items,
    'tax': tax,
    'grand_total': grand_total
  }
  return render(request, 'store/checkout.html', context)
  ### i must call user profile to pass this into the template







### we will store the cart id in the database
### the cart id is the session id (but it is stored in the cookies and it says "3 in use")


### if you want to get all the data it is Product.objects.all()
### if you want to query some of the data it is Product.objects.get(id=product_id)
### the add to cart might be bound to the button
### product_id is got from the product we click on and we quickly use that one to get the corresponding product before going to the cart or addding it to the cart

## Just by starting the function name with an underscore it becomes a private function

## the private function _cart_id is just to extract the cart id (session id)

### get the cart using the cart id present in the session

### we can exit the page for now if we don't want to go to the cart page immediately


### {% url 'add_cart' cart_item.product.id %} 
# in the url s we have a add_cart and we are also passing in the proudct id corresponding to what we clicked
# this line in the front end is basically actuating that whole process again in this view file (which is a backend operation) // but the whole page was refreshing and i guess these are some of the reasons why we need react

### in the cart.html page the context passed into it is the cart or cart item but we can get the product from it (so this is working with both frontend and backend at the same time)

## we have assigned url 'add_cart' single_product.id to the form action and therefore after the button is hit or submitted, the form will send the information to that url and therefore we have to come and handle it in the carts/views.py file

### this the url for the product variation
### /store/category/jeans/atx-jeans/?color=blue&size=medium
# http://localhost:8000/cart/add_cart/1/?color=yellow&size=large  (as copied from the url)
## the color will come from the name in the select and the size as well and that will enter the url and we will pick it by doing request.GET['size'] or request.GET['color'] because we set it up as a get request.

## now we have the value for color and size in the database and that is what we will fetch to the user and even any number of them that the admin might set

## variation_set.all means that it will bring all the data from the variation model (it must now be variation_set.color)which is the function name

### we must have a variation manager because variation_set.all is bringing all the variations without considering where each of them should populate on the frontend

## http://127.0.0.1:8000/cart/add_cart/1/?color=red&size=small     (but i don't understand the 1 in the middle there)

## we did a GET request first so that we can test but later we did it a POST request
## there is no get request anymore and the url will not deposite of the url part of the browser (so you will not see it in the browser url part because it is a POST request and the form will handle it)

## it must not be only color and size but it must be dynamic so that in future when we add more variations it will be catered for automatically or dynamically

## this is the information about the cors that was sent along side with the post request (really beautiful)
# csrfmiddlewaretoken CTtbsmPeLKLd6gR2zYze0ddLbaxGkm5tL1ZKGl447WmXga9RmYOV1YmDb3939yL7


## in the add_cart function, we are getting the product , product variation , cart , cart item , in that order (really cool isn't it? ,,,, )
## we can use the variation to change the cart items

## the problem is that it is adding more of the variations to the same cartItem even when they are different.

## it is adding a different variation to the same cartItem and so it doesn't tell me that the item might be deleted in the admin side but rather updates it to a new variation values

## Our code must be smart enough to detect the products of the same variation in the same cartItem in our cart. if that makes sense. if it detects that the various variations are the same it must just increment the quantity rather than creating a new cartItem with that product having the same variation

## ex_var_list appeared in the server console as a query set and it must be converted to a list
## *product_variation will make sure all the product variations are added 

### the cart item is been stored based on the session id (that is when the user is not logged in)
### i went into the database as a super user (admin), and i saw a lot of carts and a lot of cartItems in the database and the carts were only stored by id and the cartItem was stored by product, variations, Cart(foreign key), quantity, is_active, 
### ah i said it, he said we will have a user field (foreign key) in the cartItem side

### as soon as we change the view function, the data going to the template will change and the cart / cartItems will pop up like magic
### as soon as we log in it takes our session and picks the cart or cartItem(i don't care) and pushes it unto the database to be assigned to that user and therefore if that user even add more items from another device kraa na it will detect he is the one and it will add up to the already existing cartItems

### in the remove_cart function (minus sign is linked to that one)
### cart = Cart.objects.get(cart_id=_cart_id(request)) must only run when the user is not logged in
### the positive sign is linked to the remove_cart_item function in the view

# C:\Users\HP\Desktop\website tutorials done\Best Django Project Ever\carts\views.py, line 173, in remove_cart_item
#   cart = Cart.objects.get(cart_id=_cart_id(request)) …
# ▶ Local vars

### we have to redirect the person to the cart page again and not to the dashboard when they are making 
### http://localhost:8000/accounts/login/?next=/cart/checkout/ this is the redirect url but we must make it dynamically (and this will all happen in the login view in the accounts app)

### the same way we handled the views.cart for authenticated user that is the same way we will handle the views.checkout for authenticated user in the carts app in the views file and we will see the cart for the authenticated user there because in actual fact only authenticated users are allowed to go there
