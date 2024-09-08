# Imports for fetching objects and rendering templates
from django.shortcuts import get_object_or_404, render

from category.models import Category  # Importing Category model
from store.models import Product  # Importing Product model


def store(request, category_slug=None):  # View function, accepts request and optional category_slug
    categories = None  # Placeholder for Category object
    products = None  # Placeholder for Product QuerySet

    # If a category_slug is provided in the URL
    if category_slug != None:
        # Fetch the category based on the slug or return 404 if not found
        categories = get_object_or_404(Category, slug=category_slug)
        # Filter products by category and check if they are available
        products = Product.objects.filter(
            category=categories, is_available=True)
        # Count the number of products
        product_count = products.count()
    else:
        # If no category_slug is provided, fetch all available products
        products = Product.objects.all().filter(is_available=True)
        # Count the number of available products
        product_count = products.count()

    # Pass the products and product count to the template context
    context = {
        'products': products,
        'product_count': product_count
    }
    # Render the 'store/store.html' template with the context data
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        # category__slug means Product category field connected category model slug field matching recieved category_slug is checking
        # next argument slug means Prodcut model slug field matching recieved product_slug as url request
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
    }

    return render(request, 'store/product_detail.html', context)
