# Importing the admin module to customize how the models are displayed in the Django admin site.
from django.contrib import admin

# Importing the Product model from the current app’s models file.
from store.models import Product


# Creating a custom admin class to define how the Product model appears in the admin site.
class ProductAdmin(admin.ModelAdmin):

    # Specifies the fields to display in the list view of the Product model in the Django admin.
    # Each of these fields will be displayed as a column.
    list_display = ('product_name', 'price', 'stock',
                    'category', 'modified_date', 'is_available')

    # Automatically populates the slug field based on the product_name field.
    # This helps in generating a URL-friendly slug without manually entering it.
    prepopulated_fields = {'slug': ('product_name',)}


admin.site.register(Product, ProductAdmin)
