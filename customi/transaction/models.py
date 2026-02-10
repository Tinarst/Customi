from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseConfig
from order.models import Order

class Payment(BaseConfig):

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        CANCELED = "canceled", _("Canceled")

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        unique=True,
        related_name="payment_order"
    )
    status = models.CharField(max_length=8, default=PaymentStatus.PENDING, choices=PaymentStatus)
    authority = models.CharField(null=True)