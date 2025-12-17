from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class AuthValidator:
    phone_validator = RegexValidator(
        regex=r"^(?:\+98|0)9\d{9}$",
        message=_("Phone number must start with 09 or +989"),
    )
    zip_code_validator = RegexValidator(
        regex=r"^\d{10}$",
        message=_("A valid postal code consists of 10 digits")
    )

class CustomUser(AbstractUser):

    class UserRole(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        CUSTOMER = 'customer', _('Customer')
        SELLER = 'seller', _('Seller')
        GUEST = 'guest', _('Guest')

    phone = models.CharField(
        unique=True,
        validators=[AuthValidator.phone_validator]
    )
    role = models.CharField(
        choices=UserRole,
        default=UserRole.CUSTOMER
    )
    
    REQUIRED_FIELDS = ['phone']
    USERNAME_FIELD = 'email'



class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    details = models.TextField()
    zip_code = models.CharField(
        unique=True,
        null=True,
        validators=[AuthValidator.zip_code_validator]
    )