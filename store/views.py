# Imports for fetching objects and rendering templates
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib import messages

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category  # Importing Category model
from orders.models import OrderProduct
from store.forms import ReviewForm
from store.models import Product, ReviewRating  # Importing Product model


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

    if request.user.is_authenticated:
        # Here we checking that this product user purchased before or not, for allowing it to write reveiw
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'reviews_count': reviews.count(),
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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # The user__id part means: "Get the id field of the related User model(Account).
            # The product__id means: "Get the id field of the related Product model.
            # so by using both we filter the ReviewRating objects based on related fields (user and product)
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            # By passing the instance also to form if the user already write a review about same product then it will rewrited
            # so thats why above we take the review, othewise user can make many reviews on single product , thats not we want
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, 'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            # if There is no review of user in this product, create new one
            # For we only pass request.POST form, the will automaically create new one
            form = ReviewForm(request.POST)
            # next we check the form valid, if valid then save to model
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, 'Thank you! Your review has been submitted')
                return redirect(url)
