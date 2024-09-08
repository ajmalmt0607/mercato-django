# Import the render function from Django's shortcuts module.
# 'render' is used to combine a template with a context and return an HTTP response.
from django.shortcuts import render

# Import the Product model from the store app's models file.
# The Product model likely represents products in your store.
from store.models import Product


# This function handles requests to the home page of the website.
def home(request):
    # Query the Product model to retrieve all products where 'is_available' is True.
    # .all() is a QuerySet method
    # filter() is a method that narrows down the QuerySet by applying conditions.
    products = Product.objects.all().filter(is_available=True)

    # Create a context dictionary containing the queried products.
    # This context will be passed to the template to render the list of available products.
    context = {
        # 'product' is the key, and 'products' is the value containing the queried products.
        'products': products,
    }

    # Render the 'home.html' template, passing in the request and the context.
    # The template will use the context to display the available products.
    return render(request, 'home.html', context=context)
