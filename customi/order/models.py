from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser, Address
from cart.models import Coupon
from stock.models import ProductStore
from core.models.base import BaseConfig


class Order(BaseConfig):

    class OrderStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        SHIPPED = "shipped", _("Shipped")
        DELIVERIED = "deliveried", _("Deliveried")
        CANCELED = "canceled", _("Canceled")

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=OrderStatus)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.DO_NOTHING, null=True, blank=True)
    total_amount = models.FloatField()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderitem_order")
    product_store = models.ForeignKey(ProductStore, on_delete=models.SET_NULL, null=True, related_name="orderitem_productstore")
    quantity = models.PositiveSmallIntegerField(editable=False)
    price = (
        models.FloatField()
    )  # do not mirroring; if one product update, it'll be change
    