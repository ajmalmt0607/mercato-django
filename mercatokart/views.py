# Import the render function from Django's shortcuts module.
# 'render' is used to combine a template with a context and return an HTTP response.
from django.shortcuts import render
from django.db.models import Avg

# Import the Product model from the store app's models file.
# The Product model likely represents products in your store.
from category.models import Category
from store.models import Product, ReviewRating


# This function handles requests to the home page of the website.
def home(request):
    # Query the Product model to retrieve all products where 'is_available' is True.
    # .all() is a QuerySet method
    # filter() is a method that narrows down the QuerySet by applying conditions.
    # products = Product.objects.all().filter(
    #     is_available=True).order_by('created_date')
    # Retrieve products that are available and order by their average review rating
    products = Product.objects.filter(is_available=True)\
        .annotate(average_rating=Avg('reviewrating__rating'))\
        .order_by('-average_rating')[:4]  # Get the top 4 products by rating
    categories = Category.objects.all()  # Fetch all categories

    # Retrieve featured products (only those marked as featured)
    featured_products = Product.objects.filter(
        is_available=True, featured=True)[:4]

    # Get the reviews
    for product in products:
        reviews = ReviewRating.objects.filter(
            product_id=product.id, status=True)

    # Create a context dictionary containing the queried products.
    # This context will be passed to the template to render the list of available products.
    context = {
        # 'product' is the key, and 'products' is the value containing the queried products.
        'products': products,
        'categories': categories,
        'reviews': reviews,
        'featured_products': featured_products,
    }

    # Render the 'home.html' template, passing in the request and the context.
    # The template will use the context to display the available products.
    return render(request, 'home.html', context=context)
