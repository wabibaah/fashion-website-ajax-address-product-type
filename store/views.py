from django.shortcuts import render, get_object_or_404, redirect
from . models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from orders.models import OrderProduct
from django.db.models import Q
from . forms import ReviewForm
from django.contrib import messages

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse

# Create your views here.

def store(request, category_slug=None):

  categories = None
  products = None

  if category_slug != None:
    categories = get_object_or_404(Category, slug = category_slug)
    products = Product.objects.filter(category=categories, is_available=True)
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
  else:
    products = Product.objects.all().filter(is_available=True).order_by('id')
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()



  context = {
    'products': paged_products,
    'product_count': product_count,
  }

  return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
  try:
    single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    
  except Exception as e:
    raise e

  if request.user.is_authenticated:
    ### checking if the user actually bought the product he wants to review
    try:
      orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    except OrderProduct.DoesNotExist:
      orderproduct = None
  
  else:
    orderproduct = None

  #get the reviews that was posted
  reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True) # in case the admin want to set the status to false he can do it because not all reviews should be allowed, the admin or product owner must have a say 

  # get the product gallery 
  ### collect static after writing the css and accept it by typing 'yes' and not 'y'
  ### we will some javascript to make sure when we click on an image it will show in the main / bigger space
  product_gallery = ProductGallery.objects.filter(product_id=single_product.id)


  
  context = {
    'single_product': single_product,
    'in_cart'       : in_cart,
    'orderproduct'  : orderproduct,
    'reviews'       : reviews,
    'product_gallery': product_gallery,
  }
  return render (request, 'store/product_detail.html', context)



def search(request):
  if 'keyword' in request.GET:
    ## in this case the keyword will store the value of jeans, shirts or any thing that was typed in the search box
    keyword = request.GET['keyword']
    if keyword:
      ### if the keyword is not blank, then do this
      products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
      product_count = products.count()

  context = {
    'products': products,
    'product_count': product_count, 
  }
  return render(request, 'store/store.html', context)


def submit_review(request, product_id):
  url = request.META.get('HTTP_REFERER')
  if request.method == 'POST':
    try:
      ### we don't want a review on this product by the same user twice/ may we update rather
      reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
      form = ReviewForm(request.POST, instance=reviews) 
      # instance = reviews is there so that a new review will not be created by the same user, so the instance must be passed
      form.save()
      messages.success(request, 'Thank you! Your review has been updated.')
      return redirect(url)

    except ReviewRating.DoesNotExist:
      form = ReviewForm(request.POST)
      if form.is_valid():
        data = ReviewRating()
        data.subject = form.cleaned_data['subject']
        data.rating = form.cleaned_data['rating']
        data.review = form.cleaned_data['review']
        data.ip = request.META.get('REMOTE_ADDR')
        data.product_id = product_id 
        data.user_id = request.user.id
        data.save()
        messages.success(request, 'Thank you! Your review has been submitted')
        return redirect(url)












### this is exactly where we render the store.html template and i am sure we can reach the database from this place (by importing the Products model here)
### you can pass the products into the template but when there are a lot of things you need to pass you can form it into a dictionary and pass it into the template in the render function call
### after adding to cart, we can change the button to be inactive and it will display (added to cart). I think this will be a good a good feature
### in the model you can set up a deleted price and even calculate a small percentage that will be shown in the frontend. Please do this as it will be very useful
### I think server side code and server side calculations can be done here

### we need to get the category of the Product (which is a foreign key in the product model) and we must also get the slug of the that Product's category
### so when we click on the product to go to the product details, we must get the product category, and we must also get the slug of that category
### underscore underscore is a synthax to get the slug of the category   category__slug 

## the double underscore(__) means that we will check the cart model, because the cart is a foreign key of the cartItem (which means that we are searching the cartItem with a foreign key)
## we will access the cart first, and with the cart (in the cartItem) we will access the cart id in the main cart model

### we went to where the product detail is and that is why we were able to see the true or false
### in_cart context is telling us whether that single product is a cart_item in the cart or not (true / false)

# 'page' is the page in the url when it comes to the pagination
### the 'paged_products' is now the number of products

## in the store function, the if statement is for when the is no slug and the else is for when the user will click on lets say shirts, jeans or anything else and it must filter according to the slug

### /store/search/ is being treated as with a category slug and the error is (no category matches the given query)
## /store/search/?keyword=shirts (this is what happens after the search function)
### the keyword comes from the name of the input

## we need to receive what is coming from the url in the case of the search parameter

## __icontains means you are searching for the keyword in that part of the model
### in django if we use the (,) it will treat it as AND because that is how the filter function works
## Q is used for complex queries

## One template which is the store.html is powered by 2 view functions, the store function and the search function and all of them render it 
### the only difference is to say if 'search' is in request.path then do something in the store.html

## in the case of product variation, a form must be created in the product_detail.html file so that it can send information about what will be choosen to the cart page or the next stage of the process


### user__id using it to search for the review means that in the reviews model there is a user and in the user model there is an id and that is what we are referring to

### NB:- if you are already logged in it must redirect you from the log in page, i must be able to do this bro

### control F5 is for hard refresh (and the color of the ratings appeared)