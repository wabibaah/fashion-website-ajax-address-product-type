from django.urls import path
from . import views


urlpatterns = [
  path('', views.store, name='store'),
  path('category/<slug:category_slug>/', views.store, name='products_by_category'),
  path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
  path('search/', views.search, name='search'),
  path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]




### in the url for slug, we are naming a variable called slug and we are saying it must match something called category slug but we don't know what that is yet
### in the url for slug, we are having a variable and giving it an alias 
### the (:) makes it dynamic
### in the views, if the category_slug is None, then we look for the category if it really exist in the Category database based on the slug which is the field name in the Category model and check if that slug matches the category_slug that is coming from the url
### after that we search for the products passing that specific category (categories in the code) to search for products under that category
### ??? Can we move move from this url to another view in another app ??  Hmmm Django for you
### 