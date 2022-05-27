from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import datetime
import json

from . models import Order, Payment, OrderProduct
from carts.models import CartItem
from . forms import OrderForm
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


def payments(request):
  body = json.loads(request.body)
  ### the information from paypal land in our frontend(browser) and we pass it through fetch to the backend and we can now take it to the payment model
  # print(body)
  order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
  ### if is_ordered is now, will the payment go through, maybe an if else or try except function can be created
  payment = Payment(
    user = request.user,
    payment_id = body['transID'],
    payment_method = body['payment_method'],
    amount_paid = order.order_total,
    status = body['status'],
  )
  payment.save()

  ### because that particular (specific) order must have a payment too / we are updating the order model too
  order.payment = payment 
  order.is_ordered = True ### because they have paid //
  order.save() 

  ### move the cart items to Order Product table
  cart_items = CartItem.objects.filter(user=request.user)

  for item in cart_items:
    orderproduct = OrderProduct()
    orderproduct.order_id = order.id
    orderproduct.payment = payment
    orderproduct.user_id = request.user.id
    orderproduct.product_id = item.product_id
    orderproduct.quantity = item.quantity
    orderproduct.product_price = item.product.price
    orderproduct.ordered = True ### after i am done i will change it order.ordered field
    orderproduct.save()

    cart_item = CartItem.objects.get(id=item.id)
    product_variation = cart_item.variations.all()
    orderproduct = OrderProduct.objects.get(id=orderproduct.id)   # we are using the id because the orderproduct has saved and therefore we can use the id
    orderproduct.variations.set(product_variation)
    orderproduct.save()

    ### reduce the quantity of the sold products
    product = Product.objects.get(id=item.product_id)
    product.stock -= item.quantity
    product.save()
    ### i checked and the atx jeans 5 (2 + 2 + 1) was reduced to give me 95 instead of 100
    ### and assignments will be if the person reverses the products we must re add them back to it
    ### you can do this and even add more models and wishlists kraa for inside bro
  
  ### clear cart
  CartItem.objects.filter(user=request.user).delete()

  ### send order received email to customer
  mail_subject = 'Thank you for your order!'
  message = render_to_string('orders/order_received_email.html', {
    'user': request.user,
    'order': order,
  })
  ### write a code to store something to proof that email was sent so that users won't lie about it
  ### also see how you can make it come in sms format
  ### how to do your own mobile money and more with sms and django
  
  to_email = request.user.email
  send_email = EmailMessage(mail_subject, message, to=[to_email])
  send_email.send()

  ### send order number and transaction id back to sendData method via JsonResponse
  data = {
    'order_number': order.order_number,
    'transID': payment.payment_id,
  }
  # print(order.order_number, payment.payment_id)
  return JsonResponse(data)
  ### this is the response we are sending back to the frontend(paypal sendData function)

  


def place_order(request, total=0, quantity=0):
  current_user = request.user  ### because we know we are already logged in so the user is in the request object

  ### if the cart count is less than or equal to 0, then redirect to the store (continue shopping)
  cart_items = CartItem.objects.filter(user=current_user)
  cart_count = cart_items.count()

  if cart_count <= 0:
    return redirect('store')

  
  grand_total = 0
  tax  = 0
  for cart_item in cart_items:
    total +=  (cart_item.product.price * cart_item.quantity)
    quantity += cart_item.quantity
  
  tax = 0.02 * total
  grand_total = total + tax



  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      ### if the form is valid, store all the billing information inside the order table
      data = Order()
      data.user              = current_user
      data.first_name        = form.cleaned_data['first_name']
      data.last_name         = form.cleaned_data['last_name']
      data.phone             = form.cleaned_data['phone']
      data.email             = form.cleaned_data['email']
      data.address_line_1    = form.cleaned_data['address_line_1']
      data.address_line_2    = form.cleaned_data['address_line_2']
      data.country           = form.cleaned_data['country']
      data.state             = form.cleaned_data['state']
      data.city              = form.cleaned_data['city']
      data.order_note        = form.cleaned_data['order_note']
      data.order_total       = grand_total
      data.tax               = tax
      data.ip                = request.META.get('REMOTE_ADDR')
      data.save()

      ### generate order number
      yr = int(datetime.date.today().strftime('%Y'))
      dt = int(datetime.date.today().strftime('%d'))
      mt = int(datetime.date.today().strftime('%m'))
      d  = datetime.date(yr, mt, dt)
      current_date = d.strftime("%Y%m%d") # 20220213   13th Feb 2022
      order_number = current_date + str(data.id)

      data.order_number      = order_number
      data.save()

      order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

      context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
      }

      return render(request, 'orders/payments.html', context)

  else:
    return redirect('checkout')


def order_complete(request):
  order_number = request.GET.get('order_number')
  transID  = request.GET.get('payment_id')  
  ## payment_id can be found in the url, but we will use them to go to the model model to fetch them (proper way of doing it)
  try:
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)

    payment = Payment.objects.get(payment_id=transID)

    subtotal = 0
    for i in ordered_products:
      subtotal += (i.product_price * i.quantity)
    
    
    


    context = {
      'order': order,
      'ordered_products': ordered_products,
      'order_number': order.order_number,
      'transID': payment.payment_id,
      'payment': payment,
      'subtotal': subtotal,
    }
    return render(request, 'orders/order_complete.html', context)
  
  except (Payment.DoesNotExist, Order.DoesNotExist):
    return redirect('home')
    
    
















### if we use filter means we can get more than one response, but if we use get means we are targeting only one response
### if you want your tax to be dynamic you can create a single model for your tax and give it one field on tax value, but for now we will set it to be static

### this is where we set the billing address and if you want to order for someone, set his name, billing address and pay for him / her or say (your loved ones)

### Because it is a foreing key in the OrderProduct, i can make it order_id instead of order or user_id instead of user
### product_price means it is a foreing(product) and the price is a field in the product

### you have to save first before you can add a many to many field. You can not add it before saving, must save first
### variations = models.ManyToManyField(Variation, blank=True) variation must be many to many in the models
### and the order products model was populated with data but not with fields (obviously) but the variations was not working yet. Guess we will fixed that.
### every cart item is stored as a product

#     raise self.model.DoesNotExist(
# orders.models.Order.DoesNotExist: Order matching query does not exist.
### i got this error which means that you cannot pay for the same order twice (you can state a message saying if you want you must order again) 
### because i think now is ordered is now True and not false
### i checked and the user was charged (False) and no new order was made for him
### 
### we want to show the user details about his order and therefore we will send it with the redirect url (from frontend) to backend and we will receive it in the order_complete view function

### the tax or functions is not working well with float so learn how to do it