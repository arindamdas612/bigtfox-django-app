from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Manger for User Profiles"""

    def create_user(self, email, initial, firstname, lastname, mobile, password=None, is_staff=False, is_superuser=False, is_active=True):
        """create a new user profile"""
        if not email:
            raise ValueError("Users must have an E-Mail Address")

        #email = self.normailze_email(email)
        user = self.model(email=email, initial=initial,
                          firstname=firstname, lastname=lastname, mobile=mobile,
                          is_staff=is_staff, is_superuser=is_superuser, is_active=is_active)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, initial, firstname, lastname, mobile, password):
        """Create and save new Super user with given detils"""
        user = self.create_user(email, initial, firstname,
                                lastname,  mobile, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name_plural = "Users"
    INITIAL_CHOICE = (
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Ms.'),
    )
    """Databse Model for the user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=20, unique=True)
    initial = models.CharField(max_length=4, choices=INITIAL_CHOICE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['initial', 'firstname', 'lastname', 'mobile']

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(User, self).save(*args, **kwargs)

    def get_full_name(self):
        """Retrieve Full name of user"""
        return f'{self.initial} {self.firstname} {self.lastname}'

    def get_formal_name(self):
        """Retrieve Full name of user"""
        return f'{self.initial} {self.lastname}, {self.firstname} '

    def get_short_name(self):
        """Retrieve Short name of user"""
        return self.firstname

    def __str__(self):
        """Return string representaion of user"""
        return self.email


class UserAddress(models.Model):
    class Meta:
        verbose_name_plural = "User Addresses"
    ADDRSS_TYPE = (
        ('Rs', 'Residence'),
        ('Of', 'Office'),
        ('Ot', 'Others'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=30)
    contact_mobile = models.CharField(max_length=15)
    line1 = models.CharField(max_length=100)
    line2 = models.CharField(max_length=100)
    line3 = models.CharField(max_length=100, blank=True, null=True)
    landmark = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    type = models.CharField(max_length=2, choices=ADDRSS_TYPE)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(UserAddress, self).save(*args, **kwargs)

    def get_address_text(self):
        full_address = f'''{self.contact_name},
{self.line1},
{self.line2},'''

        full_address = f'''{full_address}
{self.line3},''' if len(self.line3) > 0 else full_address

        full_address = f'''{full_address}
{self.landmark},
{self.district}, {self.state},
zip: {self.pincode}
Contact: {self.contact_mobile}'''
        return full_address
