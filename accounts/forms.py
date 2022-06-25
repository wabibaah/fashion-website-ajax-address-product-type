from dataclasses import fields

from django import forms
from .models import Account, Address, UserProfile


class RegistrationForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Enter Password',
    'class': 'form-control',
  }))
  confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Confirm Password',
  }))

  class Meta:
    model = Account
    fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')

    if password != confirm_password:
      raise forms.ValidationError(
        "Passwords don't match!"
      )
  
  def __init__(self, *args, **kwargs):
    super(RegistrationForm, self).__init__(*args, **kwargs)
    self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
    self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
    self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
    self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'

    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
  class Meta:
    model = Account
    fields = ['first_name', 'last_name', 'phone_number']

  def __init__(self, *args, **kwargs):
    super(UserForm, self).__init__(*args, **kwargs)

    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
  profile_picture = forms.ImageField(required=False, error_messages={'invalid': {"Image files only"}}, widget=forms.FileInput)
  class Meta:
    model = UserProfile
    # fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']
    fields = [ 'town', 'region', 'country', 'profile_picture']

  def __init__(self, *args, **kwargs):
    super(UserProfileForm, self).__init__(*args, **kwargs)

    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'

class UserAddressForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = ['full_name', 'phone', 'address_line', 'address_line2', 'town_city', 'postcode', 'region']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.fields['full_name'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Full Name'}
    )
    self.fields['phone'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Phone Number'}
    )
    self.fields['address_line'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Address Line 1'}
    )
    self.fields['address_line2'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Address Line 2'}
    )
    self.fields['town_city'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Town City'}
    )
    self.fields['postcode'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Post Code'}
    )
    self.fields['region'].widget.attrs.update(
      {'class': 'form-control mb-2 account-form', 'placeholder': 'Region'}
    )









## we can bring the fields in the model in the form 
## we can create our own fields also
# password = forms.CharField(widget=forms.PasswordInput(attrs={
#     'placeholder': 'Enter Password',
#     'class'      : 'form-control',
#   }))

## super will allow you to change how the class is saved (the original behaviour)
