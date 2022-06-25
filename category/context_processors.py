from .models import Category

def menu_links(request):
  links = Category.objects.filter(level=0)
  return dict(links=links)

# ## this is how very academy wrote his very own
# def categories(request):
#   return {
#     'categories': Category.objects.all()
#   }
#  the level is the base level for mptt 



### the context processor is here so that we can use the data in all of our templates ()