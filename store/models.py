# Importing Django's model module to create database models.
from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count

# Importing the Category model to establish a relationship with the Product model.
from accounts.models import Account
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

    def averageReview(self):
        # aggregate: A method provided by Django's QuerySet API that allows you to compute summary values (like sums, averages, counts) over a queryset.
        # Avg: This is an aggregation function provided by Django's ORM to compute the average value of a specified field across a queryset.
        reviews = ReviewRating.objects.filter(
            product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

# Custom Manager class to handle variations


class VariationManager(models.Manager):
    # Method to filter and return active color variations
    def colors(self):
        # 'super' calls the parent class's filter method with specific conditions
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    # Method to filter and return active size variations
    def sizes(self):
        # Similar to colors, but filters by 'size' instead of 'color'
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


# Tuple for specifying variation category choices (color or size)
variation_category_choice = (
    # First value is what's stored in DB, second is the display value
    ('color', 'color'),
    ('size', 'size')
)

# Main model for product variations


class Variation(models.Model):
    # Foreign key to link each variation to a specific product (many-to-one relationship)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Field to store whether the variation is a color or size, with predefined choices
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice)

    # The actual value of the variation, e.g., "Red" for color or "Large" for size
    variation_value = models.CharField(max_length=100)

    # Boolean field to indicate whether this variation is active or not
    is_active = models.BooleanField(default=True)

    # Automatically sets the current date and time when the variation is created or modified
    created_date = models.DateTimeField(auto_now=True)

    # Tells Django to use the custom manager (VariationManager) for the Variation model
    objects = VariationManager()  # Now, the methods like colors() and sizes() can be used

    def __str__(self):
        return self.variation_value  # Returns a string representation of the variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
