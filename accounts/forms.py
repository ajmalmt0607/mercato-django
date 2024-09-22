from typing import Any
from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    # Here we can create Extra fields to form we want
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control'

    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password']

    # if we having many fields to give same style, we can follow this method
    # we can also give place holder etc. also
    # Here we calling super class for changing the django default things so thats why
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        # above like also give class name element, But we having many element this is the effiecient way
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # above like also give class name element, But we having many element this is the effiecient way
        for field in self.fields:
            # then now our form fields get style
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    # This to remove current showing profile image link in edit profile form
    profile_picture = forms.ImageField(
        required=False, error_messages={'invalid': ("image files only")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2',
                  'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # above like also give class name element, But we having many element this is the effiecient way
        for field in self.fields:
            # then now our form fields get style
            self.fields[field].widget.attrs['class'] = 'form-control'
