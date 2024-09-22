from itertools import product
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# verfication email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from accounts.forms import RegistrationForm, UserForm, UserProfileForm
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _cart_id

import requests

from orders.models import Order, OrderProduct


def register(request):
    if request.method == 'POST':
        # This Request.POST contains all fields values
        form = RegistrationForm(request.POST)
        # form.is_valid means if the fields have all required data then
        if form.is_valid():
            # cleaned_data contains safe and processed form data after validation!
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Here we generating an username from email by removing after @
            username = email.split("@")[0]

            # From Account user model we create we calling the createuser function for create new user,
            # After we pass all data above to this function
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            # user function we create early had no phone number field
            # so we need to pass phone number user object seperately Here
            user.phone_number = phone_number
            user.save()

            ###################################
            # Create User Profile - Automatically to registerd user after save (means after user id generated)
            profile = UserProfile()
            profile.user_id = user.id
            # Here we setting registered user a default profile pic
            profile.profile_picture = 'default/default-user.jpg'
            profile.save()
            ####################################

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Please Activate Your Account"
            message = render_to_string(
                'accounts/account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(
            #     request, "Thank you for registering with us. we have sent you a verfication email to your email address. Please verify it.")
            return redirect('/accounts/login?command=verification&email='+email)
    else:
        # if getting get request registration form should rendered
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # using the email and password it return the user object
        user = auth.authenticate(email=email, password=password)

        # if we having user with such credential
        if user is not None:
            # Here we check if there any cartitem
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                # Check if a cart item already exists
                is_cart_item_exist = CartItem.objects.filter(
                    cart=cart).exists()
                if is_cart_item_exist:
                    # Getting the cartitem by cart ID
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variation by cart ID
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        # By Default its query set so we need to covert it list
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    # Retrieve all cart items for the product in the current cart
                    cart_item = CartItem.objects.filter(user=user)

                    # Lists to hold existing variations and item IDs from the database
                    ex_var_list = []
                    id_list = []

                    # Loop through the cart items and gather variations and IDs
                    for item in cart_item:
                        existing_variation = item.variations.all()  # Get variations for each cart item
                        # Convert to list and add to ex_var_list
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)  # Store the item ID

                    # Here check that the product variations available in existing product_variation
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            # loop through each cartitem
                            # assign the user of cartItem is current user
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, "You are now logged in")
            # this HTTP_REFERER PICK THE URL WHERE WE COME JUST BEFORE
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # print('query -->', query)
                # output : query --> next=/cart/checkout/
                # using the code we actually split into dictionary
                # like {'next' : '/cart/checkout/'}
                params = dict(x.split('=') for x in query.split('&'))
                # print('params --->', params)
                # output : params ---> {'next': '/cart/checkout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


# Activating user state
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    # if this kind of below error happens then seet user none
    except (TypeError, ValueError, Account.DoesNotExist):
        user = None
    # if the user is not none check the user token
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by(
        '-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        "orders_count": orders_count,
        "userprofile": userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            # Here we __exact we checking that the email address user entered exactly same as what we have in database
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset You Password"
            message = render_to_string(
                'accounts/reset_password_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    # if this kind of below error happens then seet user none
    except (TypeError, ValueError, Account.DoesNotExist):
        user = None

    # if the user is not none check the user token
    # purpose of checking token is to know this secure request or not
    if user is not None and default_token_generator.check_token(user, token):
        # Then next we want to save uid in session
        # Beacuse later we need this uid for resetting password
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # take the uid from the session
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            # set_password is the inbuilt function of django
            # what actually happen is,take the password and it saved in hashed format
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        # using the instance we need updating user profile not create new one
        # When the form is submitted and saved, it will update this existing user instance instead of creating a new one.
        # Without specifying instance, Django forms would assume you're trying to create a new object. By providing the existing instance, you ensure that the form updates the correct user profile.
        user_form = UserForm(request.POST, instance=request.user)
        # if we uploading any file to form we pass request.FILES parameter
        # When a form includes file uploads (like profile pictures), request.FILES contains the uploaded file data. Passing request.FILES to the form ensures that these files are processed correctly.
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        # Initialize forms with existing data for GET requests
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': userprofile,
    }

    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        # Here we taking the account object by username
        # The exact check the the current user username exact in username of db of accounts
        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # Both check_password & set_password are django's inbuilt function
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # we can also use auth.logout(request) - Then user will logout after new password set
                # and also django automatically logout the user when change the password
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
