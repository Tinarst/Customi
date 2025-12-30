from django.contrib import admin
from account.models import CustomUser, Address

admin.site.register(CustomUser)
admin.site.register(Address)