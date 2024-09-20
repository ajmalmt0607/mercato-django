# Import Django's models module to define database models
from django.db import models
# Import base classes for custom user models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# User-created function: Custom manager for Account model
class MyAccountManager(BaseUserManager):
    # User-created function: Method to create a normal user
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:  # Check if email is provided
            # Raise error if email is missing
            raise ValueError('User must have an email address')
        if not username:  # Check if username is provided
            # Raise error if username is missing
            raise ValueError('User must have a username')

        # Create a new user instance with provided details
        user = self.model(
            email=self.normalize_email(email),  # Normalize email format
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)  # Set the user's password (hashing it)
        user.save(using=self._db)  # Save the user to the database
        return user  # Return the created user

    # User-created function: Method to create a superuser (admin)
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(  # Use the create_user method to create a superuser
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # Assign superuser permissions
        user.is_admin = True
        # The is_active field is a built-in Django field for user activation.
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)  # Save the superuser to the database
        return user  # Return the created superuser

# User-created function: Custom user model


class Account(AbstractBaseUser):
    # Define fields for the user model
    first_name = models.CharField(max_length=50)  # First name field
    last_name = models.CharField(max_length=50)  # Last name field
    username = models.CharField(
        max_length=50, unique=True)  # Unique username field
    email = models.EmailField(
        max_length=100, unique=True)  # Unique email field
    phone_number = models.CharField(
        max_length=50)  # Unique phone number field

    # Required fields for user model
    date_joined = models.DateTimeField(
        auto_now_add=True)  # Timestamp when user joined
    last_login = models.DateTimeField(
        auto_now_add=True)  # Timestamp of last login
    is_admin = models.BooleanField(default=False)  # Admin status
    is_staff = models.BooleanField(default=False)  # Staff status
    # The is_active field is a built-in Django field for user activation.
    is_active = models.BooleanField(default=False)  # Active status
    is_superadmin = models.BooleanField(default=False)  # Superadmin status

    USERNAME_FIELD = 'email'  # Set email as the unique identifier for authentication
    REQUIRED_FIELDS = ['username', 'first_name',
                       'last_name']  # Additional required fields

    objects = MyAccountManager()  # Use the custom manager for this model

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    # User-created function: Return the user's email as the string representation
    def __str__(self):
        return self.email

    # User-created function: Check if the user has a specific permission (admin check)
    def has_perm(self, perm, obj=None):
        return self.is_admin  # Only admins have permissions

    # User-created function: Check if the user has permissions to view app modules
    def has_module_perms(self, add_label):
        return True  # All users have module permissions
