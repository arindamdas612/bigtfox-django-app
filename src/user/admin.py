from django.contrib import admin
from .models import User, UserAddress

admin.site.register(User)
admin.site.register(UserAddress)
