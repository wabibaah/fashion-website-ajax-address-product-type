from django.shortcuts import render, redirect, get_object_or_404
from . forms import RegistrationForm, UserForm, UserProfileForm
from . models import Account, UserProfile
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

## verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
import requests


# Create your views here.

def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      phone_number = form.cleaned_data['phone_number']
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      username = email.split('@')[0]

      user =  Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

      user.phone_number = phone_number
      user.save()

      ## account activation 
      current_site = get_current_site(request)
      mail_subject = 'Please activate your account'
      message = render_to_string('accounts/account_verification_email.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
      })

      to_email = email
      send_email = EmailMessage(mail_subject, message, to=[to_email])
      send_email.send()

      # messages.success(request, 'Thank you for registering with us. We have sent a verification email to your email address. Please verify it to activate your account.')
      return redirect('/accounts/login/?command=verification&email='+email)

  else:
    form = RegistrationForm()

  context = {
    'form': form,
  }
  return render(request, 'accounts/register.html', context)


def login(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']

    user = auth.authenticate(email=email, password=password)

    if user is not None:
      try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

        if is_cart_item_exists:
          cart_item = CartItem.objects.filter(cart=cart)

          ### getting the product variations by cart id
          product_variation = []
          for item in cart_item:
            variation = item.variations.all()
            product_variation.append(list(variation))

          ### getting the cart items from the user to access his product variations
          cart_item = CartItem.objects.filter(user=user) 
          ex_var_list = []
          id = []
          for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)
          
          # product_variation = [1, 2, 3, 4, 6]
          # ex_var_list = [4, 6, 3, 5]
          # we will look for what is common among the two and group them say ([4, 6])

          for pr in product_variation:
            if pr in ex_var_list:
              index = ex_var_list.index(pr)
              item_id = id[index]

              item = CartItem.objects.get(id=item_id)
              item.quantity += 1
              item.user = user
              item.save()

            else:
              cart_item = CartItem.objects.filter(cart=cart)
              for item in cart_item:
                item.user = user
                item.save()

      except:
        pass
      auth.login(request, user)
      messages.success(request, 'You are now logged in.')
      url = request.META.get('HTTP_REFERER')
      try:
        query = requests.utils.urlparse(url).query
        # print('Query', query)
        # next=/cart/checkout (we are spliting it into a dictionary with next as the key and the rest as the value)
        params = dict(x.split('=') for x in query.split('&'))
        # print('params ==>>>', params)
        if 'next' in params:
          nextPage = params['next']
          return redirect(nextPage)
      except:
        return redirect('dashboard')

    else:
      messages.error(request, 'Invalid login credentials')
      return redirect('login')
  return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
  auth.logout(request)
  messages.success(request, 'You are logged out.')
  return  redirect('login')


def activate(request, uidb64, token):
  try:
    ### this will give us the primary key of the user
    uid = urlsafe_base64_decode(uidb64).decode()
    user = Account._default_manager.get(pk=uid)

  except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    user.is_active = True
    user.save()

    userprofile =  UserProfile.objects.create(
      user=user, 
      address_line_1='', 
      address_line_2='', 
      city='', 
      state='', 
      country='GHANA', 
      profile_picture='/static/images/default_profile_pic.png',
    )

    userprofile.save()
    print(userprofile)
    messages.success(request, 'Congratulations! Your account is activated.')
    return redirect('login')
  else:
    messages.error(request, 'Invalid activation link')
    return redirect('register')

  
@login_required(login_url = 'login')  
def dashboard(request):
  orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
  orders_count = orders.count()

  ### this was done later kraa because we were not having the user profile by then, OK? and i fixed the error myself
  try:
    userprofile = UserProfile.objects.get(user_id=request.user.id)
  except UserProfile.DoesNotExist:
    userprofile = None
  context = {
    'orders_count': orders_count,
    'userprofile': userprofile,
  }
  return render(request, 'accounts/dashboard.html', context) 


def forgotPassword(request):
  if request.method == 'POST':
    email = request.POST['email']
    if Account.objects.filter(email=email).exists():
      user = Account.objects.get(email__iexact=email)

      ### reset password email
      current_site = get_current_site(request)
      mail_subject = 'Reset your password'
      message = render_to_string('accounts/reset_password_email.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
      })

      to_email = email
      send_email = EmailMessage(mail_subject, message, to=[to_email])
      send_email.send()

      messages.success(request, 'Password reset email has been sent to your email address.')
      return redirect('login')

    else:
      messages.error(request, 'Account does not exist!')
      return redirect('forgotPassword')
  return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
  try:
    ### this will give us the primary key of the user
    uid = urlsafe_base64_decode(uidb64).decode()
    user = Account._default_manager.get(pk=uid)

  except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    request.session['uid'] = uid
    messages.success(request, 'Please reset your password')
    return redirect('resetPassword')
  
  else:
    messages.error(request, 'This link has expired')
    return redirect('login')



def resetPassword(request):
  if request.method == 'POST':
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']

    try:

      if password == confirm_password:
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        messages.success(request, 'Password reset successful.')
        return redirect('login')
      else:
        messages.error(request, 'Passwords do not match')
        return redirect('resetPassword')

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
      messages.error(request, 'Please give us your email and we will send you a reset link')
      return redirect('forgotPassword')
    

  else:
    return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
  orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
  context = {
    'orders': orders,
  }
  return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
  userprofile = get_object_or_404(UserProfile, user=request.user)
  # try:
  #   userprofile = UserProfile.objects.get(user=request.user)
  # except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist): 
  #   userprofile = UserProfile.objects.get(user_id=request.user.id)
  
  if request.method == 'POST':
    user_form = UserForm(request.POST, instance=request.user)
    profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
    print(userprofile)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      profile_form.save()
      messages.success(request, 'Your profile has been updated!')
      return redirect('edit_profile')
  
  else:
    print(userprofile)
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=userprofile)
  
  context = {
    'user_form': user_form,
    'profile_form': profile_form,
    'userprofile': userprofile,
  }
  
  return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
  if request.method == 'POST':
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    user = Account.objects.get(username__exact=request.user.username)

    if new_password == confirm_password:
      success = user.check_password(current_password)

      if success:
        user.set_password(new_password)
        user.save()
        ## auth.logout(request) if you want to logout out the person so that they can login again with their new password (django will even log you out by default)
        messages.success(request, 'Password updated successfully.')
        return redirect('change_password')

      else:
        ### if the current password is not correct
        messages.error(request, 'Please enter your current password correctly.')
        return redirect('change_password')

    else:
      ## if the new password and the confirm passwords are not the same
      messages.error(request, 'Passwords do not match.')
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




























## we will use django model forms to replicate the data in the model
## request.POST will contain all the field values
## in the accounts model file, we have the create_user and create_superuser functions and we are leveraging it
## in the else case means it is just a GET request and hence it should render just the form
## if you get to the page first, it is a get request and the registration form will render and it you submit the form it will parse it to the request.POST and it will create a user in the views(controller) and a pre defined model function

## in the installed apps we have django messages and it is the default one installed in django for us to use

## it will first check if the user is logged in before executing the logout functionality

### we save the user but we don't activate it until we send the email, the click the link to verify who they are (smooth)
### the superuser has the is_active part true by default but the rest we sign up through the website doesn't have that by default (but we will do that when they activate their account)
## we will encode the primary key into uid but when we are activating the account we will decode it (from the encoded version)
### the library is default_token_generator and it has make_token and check token functions

### we have created an activation link in the email template and we must create a url for it. That means that this whole activate link comes back into our url, views and the model (database). Amazing .... bro

### in the activate function, we have the uidb64 and the token is coming in the from the url or link in the email and that enters the function and we will pick it up with the parameters in the functions

### http://localhost:8000/accounts/login/?command=verification&email=mkdbaah@gmail.com
### if there is a command of verification, then we are going to show the signin box again for the person(user) to type anything inside again
### if the command is not there then we show the signin page

### email = request.POST['email']  , the email in the quotes that we are accessing is from the name in the html file

### supposed to be Account.objects.get(email=email) but it is rather 'email__iexact=email' so that it will be exact and the i will make it case insentitive

### in the resetPassword function, we don't need to pass the uidb64 becasuse it is already stored in the session
### in the resetPassword function, i will set a try catch block to cater for the error

### there will be no user assigned to the cartItem (cart) until we log in

### when we are not logged in we can show the cartItems based on the cart id, but when we are logged in, we should show the cartItems according to the user it belongs to

### when we are clicking on login it should group the items with the same product variation

### request.META.get('HTTP_REFERER')   will grab the previous url where you came from
### params ==>>> {'next': '/cart/checkout/'}

## you have to make a view function for every dashboard link? wow great.

### for css purpose we created an html form for now
### the model forms are going to be passed as a context oo (tsaii)

### exact is case sensitive and iexact is case insensitive

### Before deplaying please change debug = False in the django settings

### we must fix the error of the user not having a profile picture
### We must fix the issue of the user not pay for the same order twice 
