# Importing Django's model module to create database models.
from django.db import models
from django.urls import reverse

# Importing the Category model to establish a relationship with the Product model.
from category.models import Category


# Defining the Product model (database table) by inheriting from models.Model.
class Product(models.Model):

    # Field to store the product name, with a maximum length of 200 characters.
    # The 'unique=True' ensures that each product name is unique in the database.
    product_name = models.CharField(max_length=200, unique=True)

    # SlugField generates a URL-friendly version of the product name (for clean URLs).
    slug = models.SlugField(max_length=200, unique=True)

    # Description of the product. It's a text field that allows up to 200 characters.
    description = models.TextField(max_length=200, blank=True)

    # Price of the product stored as an integer value.
    price = models.IntegerField()

    # Image field to upload the product image.
    # The 'upload_to' argument specifies the folder where images will be uploaded.
    images = models.ImageField(upload_to='photos/products')

    # Stock quantity of the product, stored as an integer.
    stock = models.IntegerField()

    # Boolean field indicating whether the product is available.
    is_available = models.BooleanField(default=True)

    # Foreign key establishes a relationship with the Category model.
    # Each product belongs to one category, and 'on_delete=models.CASCADE' ensures that
    # if a category is deleted, all related products are also deleted (cascading delete).
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Automatically sets the field to the current date when the product is created.
    # The date doesn't change after creation.
    created_date = models.DateField(auto_now_add=True)

    # Automatically updates the field to the current date each time the product is saved.
    modified_date = models.DateField(auto_now=True)

    # This is the function for products goto single page
    # reverse method first argument is product_detail its url name
    # first argument is self.category.slug category field slug field and next category slug field
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    # This method defines how the product is represented as a string.
    # When a product instance is printed or displayed (e.g., in the Django admin),
    # it will show the product's name instead of the default object representation.

    def __str__(self):
        return self.product_name
