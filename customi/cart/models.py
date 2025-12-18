from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser
from stock.models import ProductStore
from datetime import datetime


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_store = models.ForeignKey(ProductStore, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Coupon(models.Model):

    class CouponType(models.TextChoices):
        PERCENT = "percent", _("Percentage")
        UNIT = "unit", _("Currency unit")

    created_at = models.DateTimeField(default=datetime.now)
    expire_date = models.DateField(null=True)
    expire_time = models.TimeField(null=True)
    type = models.CharField(max_length=10, default=CouponType.PERCENT, choices=CouponType)
