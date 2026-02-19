from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser, Address
from cart.models import Coupon
from stock.models import ProductStore
from core.models.base import BaseConfig


class OrderManager(models.Manager):
    def create(self, user: CustomUser, shipping_address):
        cart = user.cart_user
        total_amount = cart.total_price
        order = Order(
            user=user,
            status=Order.OrderStatus.PENDING,
            shipping_address=shipping_address,
            total_amount=total_amount,
        )

        order.save()

        for item in cart.cartitem_cart.all():
            OrderItem.objects.create(
                order=order,
                product_store=item.product_store,
                quantity=item.quantity,
                price=item.total_price,
            )
        return order


class Order(BaseConfig):

    class OrderStatus(models.IntegerChoices):
        PENDING = 1, _("Pending")
        PAID = 2, _("Paid")
        SHIPPED = 3, _("Shipped")
        CANCELED = 4, _("Canceled")

    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="order_user"
    )
    status = models.IntegerField(choices=OrderStatus)
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_shipping_address",
    )
    coupon = models.ForeignKey(
        Coupon, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    total_amount = models.FloatField()

    objects = OrderManager()


class OrderItemManager(models.Manager):
    def change_status(self, order: Order, status=Order.OrderStatus.PAID):
        order_items = self.filter(order=order)
        for item in order_items:
            item.status = order.status
            item.save()

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderitem_order"
    )
    product_store = models.ForeignKey(
        ProductStore,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orderitem_productstore",
    )
    quantity = models.PositiveSmallIntegerField(default=1, editable=False)
    price = (
        models.FloatField()
    )  # do not mirroring; if one product update, it'll be change
    status = models.IntegerField(choices=Order.OrderStatus, default=Order.OrderStatus.PENDING)
    
    objects = OrderItemManager()
