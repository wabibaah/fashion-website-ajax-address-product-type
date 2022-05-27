from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
  products = Product.objects.all().filter(is_available=True).order_by('created_date') #remember - later

  reviews = 0  ### causing problems but made me learn about database migrations on the server

  for product in products:
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

  context = {
    'products': products,
    'reviews': reviews,
  }
  return render(request, 'home.html', context)





### products is got from the database which is original in django (not mongodb) 
### the context is just so that we can pass information about the products into the home page
### the home page is handled by the greatkart (main) view.py file and I don't know why
### the data is got from the views.py file and that same views.py file gives the data to the home.html template in the template folder