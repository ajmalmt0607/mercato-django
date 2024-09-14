# Import necessary functions and models from Django and your app
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem  # Import Cart and CartItem models
# Import Product and Variation models
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist


# Helper function to get or create the cart ID from the user's session
def _cart_id(request):
    # Retrieve the session key, which is used as the cart ID
    cart = request.session.session_key
    # If no session exists, create one (session key is generated)
    if not cart:
        cart = request.session.create()
    return cart  # Return the session key as the cart ID


# Function to add a product to the cart
def add_cart(request, product_id):
    # Retrieve the product based on its ID
    product = Product.objects.get(id=product_id)
    product_variation = []

    # Check if the request method is POST to capture form data
    if request.method == 'POST':
        for item in request.POST:
            key = item  # Form field name (like 'color' or 'size')
            # Form field value (e.g., 'Red', 'Medium')
            value = request.POST[key]

            # Try to match a variation in the database for the product
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,  # Case-insensitive match for the category
                    variation_value__iexact=value  # Case-insensitive match for the value
                )
                # Add the found variation to the list
                product_variation.append(variation)
            except:
                pass  # Ignore any variation that doesn't match

    # Try to get the Cart object associated with the current session
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # If the cart doesn't exist, create a new one with the current session ID
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()  # Save the cart instance

    # Check if a cart item for the specific product already exists
    is_cart_item_exist = CartItem.objects.filter(
        product=product, cart=cart).exists()

    if is_cart_item_exist:
        # Retrieve all cart items for the product in the current cart
        cart_items = CartItem.objects.filter(product=product, cart=cart)

        # Lists to hold existing variations and item IDs from the database
        ex_var_list = []
        id_list = []

        # Loop through the cart items and gather variations and IDs
        for item in cart_items:
            existing_variation = item.variations.all()  # Get variations for each cart item
            # Convert to list and add to ex_var_list
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)  # Store the item ID

        # Check if the current product variations already exist in the cart
        if product_variation in ex_var_list:
            # If found, get the corresponding cart item and increase its quantity
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]  # Get the ID of the matching cart item
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1  # Increment the quantity
            item.save()
        else:
            # If no matching variation, create a new cart item with the current variations
            item = CartItem.objects.create(
                product=product, quantity=1, cart=cart)  # Here created cartitem
            if product_variation:
                item.variations.clear()  # Clear existing variations
                # Add the new variations
                # Here we adding variations to the created item
                item.variations.add(*product_variation)
            item.save()  # then save
    else:
        # If the product is not already in the cart, create a new CartItem
        cart_item = CartItem.objects.create(
            product=product,  # Link the product to the cart item
            quantity=1,  # Set initial quantity to 1
            cart=cart  # Link the cart to the cart item
        )
        if product_variation:
            cart_item.variations.clear()  # Clear existing variations
            # Add the current variations
            cart_item.variations.add(*product_variation)
        cart_item.save()  # Save the new cart item

    # Redirect the user to the cart page after adding the item
    return redirect('cart')


# Function to decrease the quantity of a cart item or remove it if quantity is 1
def remove_cart(request, product_id, cart_item_id):
    # Get the cart object associated with the session
    cart = Cart.objects.get(cart_id=_cart_id(request))
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    try:
        # Get the cart item based on product, cart, and cart item ID
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            # Decrease the quantity if it's greater than 1
            cart_item.quantity -= 1
            cart_item.save()
        else:
            # If quantity is 1, delete the cart item
            cart_item.delete()
    except:
        pass  # Handle cases where the cart item doesn't exist

    return redirect('cart')


# Function to completely remove a cart item from the cart
def remove_cart_item(request, product_id, cart_item_id):
    # Get the cart associated with the session
    cart = Cart.objects.get(cart_id=_cart_id(request))
    # Get the product or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    # Get the specific cart item and delete it
    cart_item = CartItem.objects.get(
        product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


# Function to display the cart page with total price and quantity
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        # Get the cart object based on the session's cart ID
        cart = Cart.objects.get(cart_id=_cart_id(request))

        # Get all active cart items associated with the cart
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Loop through each cart item to calculate total price and quantity
        for cart_item in cart_items:
            # Calculate total price
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity  # Calculate total quantity

        tax = (2 * total) / 100  # Calculate 2% tax on the total
        grand_total = total + tax  # Calculate the grand total including tax

    except ObjectDoesNotExist:
        # If no cart exists, pass (an empty cart page will be rendered)
        pass

    # Create a context to pass the cart information to the template
    context = {
        'total': total,  # Total price of all items in the cart
        'quantity': quantity,  # Total quantity of all items in the cart
        'cart_items': cart_items,  # List of active cart items
        'tax': tax,  # Calculated tax
        'grand_total': grand_total,  # Grand total including tax
    }

    # Render the 'cart.html' template with the context
    return render(request, 'store/cart.html', context)
