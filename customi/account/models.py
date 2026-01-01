from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from random import randrange
from datetime import datetime, timedelta
from django.utils import timezone

from source.settings import USER_MEDIA
from core.models.base import BaseConfig


class OTPManager(models.Manager):
    @staticmethod
    def __expire_control(func):
        def wrapper(self: OTPManager, *args, **kwargs):
            data = self.select_related("user")
            if datetime.now() - self.created_at > self.expre_duration:
                self.delete()
                return None
            return func(self, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset()

    def create(self, user_phone):
        otp = OTPCenter.otp_generator()
        try:
            return super().create(otp_code=otp, user_phone=user_phone)
        except IntegrityError:
            return self.create(user_phone)


class OTPCenter(models.Model):
    otp_code = models.CharField()
    user_phone = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    expre_duration = timedelta(minutes=5)

    objects = OTPManager()

    class Meta:
        unique_together = ["otp_code", "user_phone"]

    @classmethod
    def otp_generator(cls):
        return randrange(1000, 100000, 1)

    @classmethod
    def active(cls, phone):
        """Return Boolean if active code"""
        queryset = cls.objects.filter(user_phone=phone)
        return next(
            (
                otp
                for otp in queryset
                if (timezone.now() - otp.created_at) < cls.expre_duration
            ),
            None,
        )


class AuthValidator:
    phone_validator = RegexValidator(
        regex=r"^(?:\+98|0)9\d{9}$",
        message=_("Phone number must start with 09 or +989"),
    )
    postal_code_validator = RegexValidator(
        regex=r"^\d{10}$", message=_("A valid postal code consists of 10 digits")
    )


class CustomUserManager(BaseUserManager):
    def create(self, phone, userType=None, *args, **kwargs):
        phone = CustomUser.normalize_phone(phone)
        user = CustomUser(phone=phone, *args, **kwargs)
        password = kwargs.get("password", None)
        if password is not None:
            user.set_password(password)
            
        if userType and kwargs.get("role", None) is None:
            user.role = user.UserRole.SELLER
        return user.save()

    def create_superuser(self, phone, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create(
            phone,
            username=username,
            password=password,
            role=CustomUser.UserRole.ADMIN,
            **extra_fields
        )


class CustomUser(BaseConfig, AbstractUser):

    class UserRole(models.TextChoices):
        ADMIN = "admin", _("Admin")
        CUSTOMER = "customer", _("Customer")
        SELLER = "seller", _("Seller")
        GUEST = "guest", _("Guest")

    username = models.CharField(
        _("username"), max_length=150, blank=True, null=True, unique=True
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=13, unique=True, validators=[AuthValidator.phone_validator]
    )
    role = models.CharField(max_length=8, choices=UserRole, default=UserRole.CUSTOMER)
    picture = models.ImageField(upload_to=USER_MEDIA, null=True, blank=True)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "phone"

    objects = CustomUserManager()

    @classmethod
    def normalize_phone(cls, phone):
        return "0" + phone[-10:]

    def is_seller(self):
        return True if self.role == self.UserRole.SELLER else False


class Address(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="address_user"
    )
    label = models.CharField(blank=True, help_text=_("Label for current address"))
    country = models.CharField(max_length=50, default="Iran")
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address_line_1 = models.TextField(max_length=255)
    address_line_2 = models.TextField(max_length=255, blank=True)
    postal_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        validators=[AuthValidator.postal_code_validator],
    )
