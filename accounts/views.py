from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# verfication email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from accounts.forms import RegistrationForm
from accounts.models import Account


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
            auth.login(request, user)
            # messages.success(request, "You are now logged in")
            return redirect('home')
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
        messages.success(request, 'Congratualtions! Your account is activated')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link')
        return redirect('register')
