# Importing a custom function `_cart_id` from the `carts.views` module. This function helps retrieve the current user's cart ID.
from carts.views import _cart_id
# Importing the `Cart` and `CartItem` models from the current app's `models.py`.
from .models import Cart, CartItem


# Define a function named `counter` that accepts `request` as an argument.
def counter(request):
    # Initialize the variable `cart_count` to 0. This will store the total number of items in the cart.
    cart_count = 0

    # Check if the current request's path is for the admin panel.
    if 'admin' in request.path:
        # If the path contains 'admin', return an empty dictionary. No need to count cart items for admin pages.
        return {}

    else:  # If the request is not for the admin panel:
        try:
            # Retrieve the cart(s) matching the current user's cart ID using `_cart_id`.
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            # if user is authenticated
            if request.user.is_authenticated:
                # take all the cartitems of current user
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # Get all `CartItem` objects - take the first cart cartitems in the list (using `cart[:1]`).
                cart_items = CartItem.objects.all().filter(cart=cart[:1])

            for cart_item in cart_items:  # Iterate over the retrieved `CartItem` objects.
                # Add the quantity of each `CartItem` to `cart_count`.
                cart_count += cart_item.quantity

        # Handle the case where the Cart doesn't exist (no cart for the user).
        except Cart.DoesNotExist:
            # Set `cart_count` to 0 since there's no cart and no items.
            cart_count = 0

    # Return the `cart_count` in a dictionary format (commonly used in Django templates to pass data).
    return dict(cart_count=cart_count)
