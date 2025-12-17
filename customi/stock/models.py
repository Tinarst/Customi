from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from user.models import CustomUser
from source.settings import PRODUCT_MEDIA, STORE_MEDIA
from datetime import datetime


class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Product(models.Model):
    name = models.CharField(unique=True)
    image = models.ImageField(upload_to=PRODUCT_MEDIA)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    objects = ProductManager()


class StoreManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("seller")
            .filter(seller__is_active=True)
        )


class Store(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField(default=datetime.now)  # read-only for sellers
    seller = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=STORE_MEDIA / "logo")
    description = models.TextField(null=True)

    objects = StoreManager()

    @property
    def is_active(self):
        return self.seller.is_active


class ProductStoreManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "store")
            .filter(Q(store__seller__is_active=True) & Q(product__is_active=True))
        )


class ProductStore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    price = models.FloatField()
    on_stock = models.BooleanField(default=True)
    count = models.PositiveIntegerField(null=True)
    description = models.TextField(null=True)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now)

    objects = ProductStoreManager()


class Category(models.Model):
    name = models.CharField(unique=True)
    parent = models.ForeignKey("Category", on_delete=models.CASCADE)


class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    product = models.ManyToManyField(ProductStore, related_name="wishlists")


class Feedback(models.Model):
    
    class RateChoice(models.IntegerChoices):
        ONE = 1, _('One')
        TWO = 2, _('Two')
        THREE = 3, _('Three')
        FOUR = 4, _('Four')
        FIVE = 5, _('Five')

    product_store = models.ForeignKey(ProductStore, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    rate = models.IntegerField(choices=RateChoice)
    review = models.TextField(null=True)
    created_at = models.DateTimeField(default=datetime.now)
    
    class Meta:
        unique_together = ['user', 'product_store']