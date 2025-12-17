from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser, Address
from cart.models import Coupon
from stock.models import ProductStore
from datetime import datetime


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        SHIPPED = "shipped", _("Shipped")
        DELIVERIED = "deliveried", _("Deliveried")
        CANCELED = "canceled", _("Canceled")

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=OrderStatus)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, null=True)
    total_amount = models.FloatField()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_store = models.ForeignKey(ProductStore, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    price = (
        models.FloatField()
    )  # do not mirroring; if one product update, it'll be change


class Payment(models.Model):

    class PaymentStatus(models.TextChoices):
        PAID = "paid", _("Paid")
        CANCELED = "canceled", _("Canceled")

    order = models.OneToOneField(Order, on_delete=models.PROTECT, unique=True)
    status = models.CharField(default=PaymentStatus.PAID, choices=PaymentStatus)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True, auto_now=True)
    