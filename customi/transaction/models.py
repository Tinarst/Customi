from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import BaseConfig
from order.models import Order

class Payment(BaseConfig):

    class PaymentStatus(models.TextChoices):
        PAID = "paid", _("Paid")
        CANCELED = "canceled", _("Canceled")

    order = models.OneToOneField(Order, on_delete=models.PROTECT, unique=True)
    status = models.CharField(max_length=8, default=PaymentStatus.PAID, choices=PaymentStatus)