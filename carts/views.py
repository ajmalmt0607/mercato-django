# Import necessary functions and models from Django and your app
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem  # Import Cart and CartItem models
from store.models import Product, Variation  # Import Product model
from django.core.exceptions import ObjectDoesNotExist


# Helper function to get or create the cart ID from the user's session
def _cart_id(request):
    # Get the session key, which acts as the cart ID
    cart = request.session.session_key
    # If no session exists, create one
    if not cart:
        cart = request.session.create()
    return cart  # Return the session key (cart ID)


# Function to add a product to the cart
def add_cart(request, product_id):
    # Here we getting the proudct based on its ID
    product = Product.objects.get(id=product_id)
    product_variation = []
    # Here we getting the product variation here
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product,
                                                  variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)

            except:
                pass

    # Here we getting the cart
    # Try to get the Cart associated with the current session
    try:
        # Get the Cart object that matches the current session's cart ID
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # If no Cart exists, create a new one with the current session ID
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()  # Save the cart instance

    # Check if the product already exists in the cart,
    is_cart_item_exist = CartItem.objects.filter(
        product=product, cart=cart).exists()

    if is_cart_item_exist:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # Existing variations --> database
        # current variarions --> product_variation list
        # item id --> database

        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            # this query set so we want to convert list
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        # 1. check the current product variations inside the Existing variations in db, then increase quantity
        if product_variation in ex_var_list:
            # Increase the product quantity in cart items
            # taking item id
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)
            # Add the product with different variation into cart items
            # here we adding product variation
            if len(product_variation) > 0:
                item.variations.clear()
                # star used to add all product variations
                item.variations.add(*product_variation)
            item.save()  # Save the updated CartItem
    else:
        # If the product is not already in the cart, create a new CartItem
        cart_item = CartItem.objects.create(
            product=product,  # Link the product to the cart item
            quantity=1,  # Set the initial quantity to 1
            cart=cart,  # Link the cart to the cart item
        )
        # here we adding product variation
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()  # Save the new CartItem
    # After adding the item to the cart, redirect the user to the cart page
    return redirect('cart')


# for decrement and delete from cart by minus button
def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


# remove cart item from cart when click on remove button
def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


# Function to display the cart page
def cart(request, total=0, quantity=0, cart_items=None):
    """
    This function calculates the total price and total quantity of items
    in the user's cart and renders the cart page.
    """
    try:
        # Get the cart object based on the session's cart_id
        cart = Cart.objects.get(cart_id=_cart_id(request))

        # Get all active cart items (is_active=True) associated with the user's cart
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Loop through each cart item to calculate total cost and quantity
        for cart_item in cart_items:
            # Calculate the total price by multiplying product price by quantity
            total += (cart_item.product.price * cart_item.quantity)

            # Increment the total quantity
            quantity += cart_item.quantity

        # 2 percentage tax on total value
        tax = (2 * total)/100
        grand_total = total + tax

    # Handle the case where the Cart object does not exist (e.g., for new users)
    except ObjectDoesNotExist:
        # Simply pass because we may render an empty cart in this case
        pass

    # Create a context dictionary to pass calculated total, quantity, and cart items to the template
    context = {
        'total': total,  # Total price of all items in the cart
        'quantity': quantity,  # Total quantity of all items in the cart
        'cart_items': cart_items,  # List of active cart items
        'tax': tax,
        'grand_total': grand_total,
    }

    # Render the 'cart.html' template, passing in the context to display cart info
    return render(request, 'store/cart.html', context)
