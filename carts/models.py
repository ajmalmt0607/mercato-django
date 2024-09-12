from django.db import models

from store.models import Product, Variation


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    # auto_now_add means automatically sets the field to the current date/time only when the object is first created
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


# Defining the CartItem model, which represents an item in a shopping cart
class CartItem(models.Model):
    # ForeignKey relationship to the Product model. This creates a many-to-one relationship,
    # meaning each CartItem is linked to one Product, but a Product can be in many CartItems.
    # 'on_delete=models.CASCADE' ensures that if the related Product is deleted,
    # all associated CartItems will also be deleted.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # many products has same variation so thats why we use Many to Many Field
    variations = models.ManyToManyField(Variation, blank=True)

    # ForeignKey relationship to the Cart model. This links each CartItem to a specific Cart.
    # 'on_delete=models.CASCADE' means if the Cart is deleted, the CartItems associated with
    # that Cart will also be deleted.
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    # Integer field to store the quantity of the product in the cart. This represents
    # how many units of the product are added to the cart.
    quantity = models.IntegerField()

    # Boolean field to track whether the CartItem is active or not.
    # Default is set to True, meaning the CartItem is considered active when created.
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    # A special method that defines how this object is represented as a string.
    # This will return the product name or representation when the CartItem is converted to a string.
    def __unicode__(self):
        # Return the product's string representation (usually defined in the Product model's __str__ method).
        # Make sure to cast product to string to avoid errors
        return str(self.product)
