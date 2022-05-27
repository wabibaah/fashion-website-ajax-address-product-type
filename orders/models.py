from django.db import models
from accounts.models import Account
from store.models import Product, Variation


# Create your models here.

class Payment(models.Model):
  user           = models.ForeignKey(Account, on_delete=models.CASCADE)
  payment_id     = models.CharField(max_length=100)
  payment_method = models.CharField(max_length=100)
  amount_paid    = models.CharField(max_length=100)
  status         = models.CharField(max_length=100)
  created_at     = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.payment_id

class Order(models.Model):
  STATUS = (
    ('New', 'New'),
    ('Accepted', 'Accepted'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
  )

  user           = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
  payment        = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  order_number   = models.CharField(max_length=20)
  first_name     = models.CharField(max_length=50)
  last_name      = models.CharField(max_length=50)
  phone          = models.CharField(max_length=50)
  email          = models.EmailField(max_length=50)
  address_line_1 = models.CharField(max_length=50)
  address_line_2 = models.CharField(max_length=50, blank=True)
  country        = models.CharField(max_length=50)
  state          = models.CharField(max_length=50)
  city           = models.CharField(max_length=50)
  order_note     = models.CharField(max_length=100, blank=True)
  order_total    = models.FloatField()
  tax            = models.FloatField()
  status         = models.CharField(max_length=10, choices=STATUS, default='New')
  ip             = models.CharField(blank=True, max_length=20)
  is_ordered     = models.BooleanField(default=False)
  created_at     = models.DateTimeField(auto_now_add=True)
  updated_at     = models.DateTimeField(auto_now=True)

  def full_name(self):
    return f'{self.first_name} {self.last_name}'

  def full_address(self):
    return f'{self.address_line_1} {self.address_line_2}'


  def __str__(self):
    return self.first_name


class OrderProduct(models.Model):
  order          = models.ForeignKey(Order, on_delete=models.CASCADE)
  payment        = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  user           = models.ForeignKey(Account, on_delete=models.CASCADE)
  product        = models.ForeignKey(Product, on_delete=models.CASCADE)
  variations = models.ManyToManyField(Variation, blank=True)
  # color          = models.CharField(max_length=50)
  # size           = models.CharField(max_length=50)  this size and color is cartered for in the variation already dummy
  quantity       = models.IntegerField()
  product_price  = models.FloatField()
  ordered        = models.BooleanField(default=False)
  created_at     = models.DateTimeField(auto_now_add=True)
  updated_at     = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.product.product_name





### we must grab all the information about the payment from paypal that we console logged into the payment model

# Capture result Objectcreate_time: "2022-02-14T09:35:58Z"id: "99C97108N4460334E"intent: "CAPTURE"links: Array(1)0: {href: 'https://api.sandbox.paypal.com/v2/checkout/orders/99C97108N4460334E', rel: 'self', method: 'GET'}length: 1[[Prototype]]: Array(0)payer: address: {country_code: 'US'}country_code: "US"[[Prototype]]: Objectemail_address: "sb-kfoao7192083@personal.example.com"name: {given_name: 'John', surname: 'Doe'}given_name: "John"surname: "Doe"[[Prototype]]: Objectpayer_id: "VCEX568H845ZY"[[Prototype]]: Objectconstructor: ƒ Object()hasOwnProperty: ƒ hasOwnProperty()isPrototypeOf: ƒ isPrototypeOf()propertyIsEnumerable: ƒ propertyIsEnumerable()toLocaleString: ƒ toLocaleString()toString: ƒ toString()valueOf: ƒ valueOf()__defineGetter__: ƒ __defineGetter__()__defineSetter__: ƒ __defineSetter__()__lookupGetter__: ƒ __lookupGetter__()__lookupSetter__: ƒ __lookupSetter__()__proto__: (...)get __proto__: ƒ __proto__()set __proto__: ƒ __proto__()purchase_units: [{…}]0: {reference_id: 'default', amount: {…}, payee: {…}, shipping: {…}, payments: {…}}length: 1[[Prototype]]: Array(0)status: "COMPLETED"update_time: "2022-02-14T09:36:32Z"[[Prototype]]: Objectconstructor: ƒ Object()hasOwnProperty: ƒ hasOwnProperty()isPrototypeOf: ƒ isPrototypeOf()propertyIsEnumerable: ƒ propertyIsEnumerable()toLocaleString: ƒ toLocaleString()toString: ƒ toString()valueOf: ƒ valueOf()__defineGetter__: ƒ __defineGetter__()__defineSetter__: ƒ __defineSetter__()__lookupGetter__: ƒ __lookupGetter__()__lookupSetter__: ƒ __lookupSetter__()__proto__: (...)get __proto__: ƒ __proto__()set __proto__: ƒ __proto__() {
#   "id": "99C97108N4460334E",
#   "intent": "CAPTURE",
#   "status": "COMPLETED",
#   "purchase_units": [
#     {
#       "reference_id": "default",
#       "amount": {
#         "currency_code": "USD",
#         "value": "2029.80"
#       },
#       "payee": {
#         "email_address": "serngreatkart.businesssandbox@gmail.com",
#         "merchant_id": "M9LV6XU9R4TSA"
#       },
#       "shipping": {
#         "name": {
#           "full_name": "John Doe"
#         },
#         "address": {
#           "address_line_1": "1 Main St",
#           "admin_area_2": "San Jose",
#           "admin_area_1": "CA",
#           "postal_code": "95131",
#           "country_code": "US"
#         }
#       },
#       "payments": {
#         "captures": [
#           {
#             "id": "47230985YR544431G",
#             "status": "COMPLETED",
#             "amount": {
#               "currency_code": "USD",
#               "value": "2029.80"
#             },
#             "final_capture": true,
#             "seller_protection": {
#               "status": "ELIGIBLE",
#               "dispute_categories": [
#                 "ITEM_NOT_RECEIVED",
#                 "UNAUTHORIZED_TRANSACTION"
#               ]
#             },
#             "create_time": "2022-02-14T09:36:32Z",
#             "update_time": "2022-02-14T09:36:32Z"
#           }
#         ]
#       }
#     }
#   ],
#   "payer": {
#     "name": {
#       "given_name": "John",
#       "surname": "Doe"
#     },
#     "email_address": "sb-kfoao7192083@personal.example.com",
#     "payer_id": "VCEX568H845ZY",
#     "address": {
#       "country_code": "US"
#     }
#   },
#   "create_time": "2022-02-14T09:35:58Z",
#   "update_time": "2022-02-14T09:36:32Z",
#   "links": [
#     {
#       "href": "https://api.sandbox.paypal.com/v2/checkout/orders/99C97108N4460334E",
#       "rel": "self",
#       "method": "GET"
#     }
#   ]
# }
#
