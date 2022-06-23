

from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.

class Category(MPTTModel):
  category_name = models.CharField(
    verbose_name=("Category Name"),
    help_text=("Required and Unique"),
    max_length=50, 
    unique=True
  )
  slug = models.SlugField(verbose_name=("Category safe URL"), max_length=100, unique=True)
  parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
  is_active = models.BooleanField(default=True)
  description = models.TextField(max_length=255, blank=True)
  cat_image = models.ImageField(upload_to='photos/categories', blank=True)

  class MPTTMeta:
    order_insertion_by = ['category_name']

  class Meta:
    verbose_name = 'category'
    verbose_name_plural = 'categories'

  def get_url(self):
    return reverse('products_by_category', args=[self.slug])

  def __str__(self):
    return self.category_name
# class Category(models.Model):
#   category_name = models.CharField(max_length=50, unique=True)
#   slug = models.SlugField(max_length=100, unique=True)
#   description = models.TextField(max_length=255, blank=True)
#   cat_image = models.ImageField(upload_to='photos/categories', blank=True)

#   class Meta:
#     verbose_name = 'category'
#     verbose_name_plural = 'categories'

#   def get_url(self):
#     return reverse('products_by_category', args=[self.slug])

#   def __str__(self):
#     return self.category_name





#### the get url function takes the name given to the url in the category.urls.py file, and takes an instance of the slug