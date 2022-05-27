from .models import Category

def menu_links(request):
  links = Category.objects.all()
  return dict(links=links)




### the context processor is here so that we can use the data in all of our templates ()