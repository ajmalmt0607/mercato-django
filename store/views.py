# Imports for fetching objects and rendering templates
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category  # Importing Category model
from store.models import Product  # Importing Product model


# def store(request, category_slug=None):  # View function, accepts request and optional category_slug
#     categories = None  # Placeholder for Category object
#     products = None  # Placeholder for Product QuerySet

#     # If a category_slug is provided in the URL
#     if category_slug != None:
#         # Fetch the category based on the slug or return 404 if not found
#         categories = get_object_or_404(Category, slug=category_slug)
#         # Filter products by category and check if they are available
#         products = Product.objects.filter(
#             category=categories, is_available=True)
#         # Count the number of products
#         product_count = products.count()
#     else:
#         # If no category_slug is provided, fetch all available products
#         products = Product.objects.all().filter(is_available=True)
#         # Count the number of available products
#         product_count = products.count()

#     # Pass the products and product count to the template context
#     context = {
#         'products': products,
#         'product_count': product_count
#     }
#     # Render the 'store/store.html' template with the context data
#     return render(request, 'store/store.html', context)


def store(request, category_slug=None):
    categories = None
    products = None

    # Fetch products based on the category slug if provided
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        # paginator code
        paginator = Paginator(products, 6)
        page = request.GET.get('page')  # Here get the page= value
        # here from all product above we take only 6, then we send this context
        # for ot find previous and next page
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(
            is_available=True).order_by('id')  # here we getting all products
        # paginator code
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        # here from all product above we take only 6, then we send this context
        # for ot find previous and next page
        paged_products = paginator.get_page(page)

    # Get all the products in the cart for the current session in a single query
    cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))

    # Create a set of product IDs in the cart for fast lookup
    cart_product_ids = set(cart_items.values_list('product_id', flat=True))

    # Prepare the context with the product data and their cart status
    context = {
        'products':  paged_products,
        'cart_product_ids': cart_product_ids,  # Set of product IDs in the cart
        'product_count': products.count(),  # using product count function we get count
    }

    # Render the template with the product list and in-cart info
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        # category__slug means Product category field connected category model slug field matching recieved category_slug is checking
        # next argument slug means Prodcut model slug field matching recieved product_slug as url request
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        # Here checking that this product is already in cartitems
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:  # first we checking if there is any keyword
        keyword = request.GET['keyword']  # then taking that keyword
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    context = {
        'products': products,
        'product_count': products.count(),  # using product count function we get count
    }
    return render(request, 'store/store.html', context)
