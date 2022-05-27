from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

## CREATING A MODEL FOR SUPER ADMIN 
class MyAccountManager(BaseUserManager):

  ### this is for creating a normal user
  def create_user(self, first_name, last_name, username, email, password=None):
    if not email:
      raise ValueError('User must have an email address')
    
    if not username:
      raise ValueError('User must have a username')
    
    user = self.model(
      email = self.normalize_email(email),
      username = username,
      first_name = first_name,
      last_name = last_name
    )

    user.set_password(password)
    user.save(using=self._db)
    return user

  ### this is for creating a super user
  def create_superuser(self, first_name, last_name, email, username, password):
    user = self.create_user(
      email = self.normalize_email(email),
      username = username,
      password = password,
      first_name = first_name,
      last_name = last_name
    )
    user.is_admin = True
    user.is_active = True
    user.is_staff = True
    user.is_superadmin = True
    user.save(using=self._db)
    return user

    ### i guess with this above two creating methods i can create more types of users



class Account(AbstractBaseUser):
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  username = models.CharField(max_length=50, unique=True)
  email = models.EmailField(max_length=100, unique=True)
  phone_number = models.CharField(max_length=50)

  #REQUIRED
  date_joined = models.DateTimeField(auto_now_add=True)
  last_login = models.DateTimeField(auto_now_add=True)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  is_superadmin = models.BooleanField(default=False)

  #USING EMAIL TO LOGIN INSTEAD OF USERNAME(which is old school)
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

  ## We need to tell this Account that we are using the MyAccountManager that to create the above two accounts(normal user and a super user)
  objects = MyAccountManager()

  # we made this just to call it in the user reviews html page. we can also make the total = price * quantity here
  def full_name(self):
    return f'{self.first_name} {self.last_name}'

  def __str__(self):
    return self.email

  def has_perm(self, perm, obj=None):
    return self.is_admin

  def has_module_perms(self, add_label):
    return True


class UserProfile(models.Model):
  user = models.OneToOneField(Account, on_delete=models.CASCADE) # you can have only one profile for only one account
  address_line_1 = models.CharField( blank=True , max_length=100)
  address_line_2 = models.CharField(blank=True , max_length=100)
  profile_picture = models.ImageField(default='default_profile_pic.png', upload_to='userprofile', blank=True, null=True)
  city = models.CharField(max_length=20)
  state = models.CharField(max_length=20)
  country = models.CharField(max_length=20)

  def __str__(self):
    return self.user.first_name   
    ### the user is in the UserProfile and the first_name is in the Account  model

  def full_address(self):
    return f'{self.address_line_1} {self.address_line_2}'



## delete the existing database (db.sqlite3)
## run python manage.py runserver first so that the empty db.sqlite3 will show up
## instead of the usual username it is now asking for the email (very cool but boiler plate code)
