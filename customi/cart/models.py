from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db.models.functions import Coalesce
from account.models import CustomUser
from stock.models import ProductStore
from datetime import datetime, time
import random
import string


class Cart(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="cart_user"
    )

    @property
    def total_price(self):
        items = self.cartitem_cart.all()
        if items.exists():
            total_price = sum(
                product.total_price for product in self.cartitem_cart.all()
            )
            return total_price
        return 0.0

    @property
    def total_discount(self):
        items = self.cartitem_cart.all()
        if items.exists():
            return sum(product.total_discount for product in self.cartitem_cart.all())
        return 0.0


class CartItemManager(models.Manager):
    def create(self, cart, product_store):
        try:
            cart_item = self.get(cart=cart, product_store=product_store)
        except CartItem.DoesNotExist:
            cart_item = self.model(cart=cart, product_store=product_store)
        else:
            cart_item.quantity += 1
        finally:
            cart_item.save()
            return cart_item


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cartitem_cart"
    )
    product_store = models.ForeignKey(
        ProductStore, on_delete=models.CASCADE, related_name="cartitem_productstore"
    )
    quantity = models.IntegerField(default=1)

    objects = CartItemManager()

    @property
    def total_price(self):
        price = self.product_store.price
        return price * self.quantity - self.total_discount

    @property
    def total_discount(self):
        discount_price = self.product_store.discount_price
        if discount_price:
            discount = self.product_store.price - discount_price
            if discount > 0.0:
                return discount * self.quantity
        return 0.0


class Coupon(models.Model):

    class CouponType(models.TextChoices):
        PERCENT = "percent", _("Percentage")
        UNIT = "unit", _("Currency unit")

    code = models.CharField(max_length=12, blank=True)
    value = models.FloatField()
    usage_limit = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.now)
    expire_date = models.DateField(null=True)
    expire_time = models.TimeField(default=time(0, 0))
    type = models.CharField(
        max_length=10, default=CouponType.PERCENT, choices=CouponType
    )

    @property
    def expire_at(self):
        if self.expire_date:
            return datetime.combine(self.expire_date, self.expire_time)
        return None

    @property
    def is_active(self):
        if self.expire_at:
            return bool(self.expire_at > datetime.now())
        return True

    @property
    def __random_code(self):
        chars = string.ascii_letters + string.digits
        code = "".join(random.choices(chars, 12))
        return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.__random_code
        return super().save(*args, **kwargs)
