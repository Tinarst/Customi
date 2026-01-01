from django.db import models
from django.db.models import Q, Avg, Count, Sum, Min, QuerySet, Max, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser
from source.settings import PRODUCT_MEDIA, PRODUCT_CATEGORY_MEDIA, STORE_MEDIA
from datetime import datetime
from core.models.base import BaseConfig


class CategoryManager(models.Manager): ...



class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to=PRODUCT_CATEGORY_MEDIA, null=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "Category", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name



class ProductImage(models.Model):
    image = models.ImageField(upload_to=PRODUCT_MEDIA)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="productimage_product"
    )

class ProductQuerySet(QuerySet):
    def with_best_seller(self):
        productstore_subquery = (
            ProductStore
            .objects
            .filter(product=OuterRef("pk"))
            .annotate(total_sold=Coalesce(Sum("orderitem_productstore__quantity"), 0))
            .order_by("-total_sold")
        ).values("pk")[:1]

        return (
            self
            .annotate(
                best_seller=Subquery(productstore_subquery)
            )
        )
    
    def with_rating(self):
        return (
            self
            .annotate(
                rating=Coalesce(Avg("productfeedback_product__rating"), 0.0)
            )
        )
    
    def with_best_price(self):
        return (
            self
            .annotate(
                best_price=Coalesce(Min("productstore_product__price"), 0.0)
            )
        )
    
    def with_stock(self):
        return (
            self
            .annotate(
                stock=Coalesce(Sum("productstore_product__stock"), 0)
            )
        )
    
    def products_with_parent(self, category: int):
        categories = set()
        
        def get_category(category):
            categories.add(category)
            category = Category.objects.get(pk=int(category))
            children_cat = category.category_set.all().values_list("pk", flat=True)
            for child in children_cat:
                if child not in categories:
                    get_category(child)
            
        
        get_category(int(category))

        return (
            self
            .filter(
                category__id__in=categories
            )
        )




class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db).select_related("category").filter(is_active=True)


    def with_rating(self):
        """Return product queryset include avg rate"""

        return self.get_queryset().with_rating()


    def with_best_price(self):
        """Return product queryset include best productstore price"""
        
        return self.get_queryset().with_best_price()


    def with_stock(self):
        """Return product queryset include count of instock productstore"""
        
        return self.get_queryset().with_stock()
    
        
    def products_with_parent(self, category, parent=None):
        return (
            self
            .get_queryset()
            .products_with_parent(category)
        )
        


class Product(BaseConfig):
    name = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        to="Category",
        on_delete=models.CASCADE,
        null=True,
        related_name="product_category",
    )
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    objects = ProductManager()


    @staticmethod
    def active_filtering(func):
        def wrapper(self, *args, **kwargs):
            active = self.is_active
            if active:
                return func(self, *args, **kwargs)
            return None

        return wrapper


    @property
    @active_filtering
    def best_seller(self):
        best = (
            self
            .productstore_product
            .annotate(
                total_sold=Coalesce(Sum("orderitem_productstore__quantity"), 0)
            )
            .order_by("-total_sold", "price")
            .first()
        )
        return best if best else None
    
    def __str__(self):
        return self.name



class StoreManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("seller")
            .filter(seller__is_active=True)
        )


class Store(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=datetime.now)  # read-only for sellers
    seller = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=f"{STORE_MEDIA}/logo")
    description = models.TextField(null=True)

    objects = StoreManager()

    @property
    def is_active(self):
        return self.seller.is_active
    
    def __str__(self):
        return self.name


class ProductStoreManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "store")
            .filter(store__seller__is_active=True)
        )

    def best_price(self):
        return self.get_queryset().select_related("product").order_by("-price")


class ProductStore(BaseConfig):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="productstore_product"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="productstore_store"
    )
    price = models.FloatField()
    stock = models.PositiveIntegerField(null=True)
    discount_price = models.FloatField(null=True, blank=True)

    objects = ProductStoreManager()
    
    def __str__(self):
        return f"from {self.store} have {self.product}"


class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    product = models.ManyToManyField(ProductStore, related_name="wishlists")


class Feedback(models.Model):

    class RatingChoice(models.IntegerChoices):
        ONE = 1, _("One")
        TWO = 2, _("Two")
        THREE = 3, _("Three")
        FOUR = 4, _("Four")
        FIVE = 5, _("Five")

    rating = models.IntegerField(choices=RatingChoice)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class ProductFeedback(Feedback):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="productfeedback_product"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="productfeedback_user"
    )
    
    def __str__(self):
        return f"user {self.user} to {self.product.name}"

class StoreFeedback(Feedback):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="storefeedback_store"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="storefeedback_user"
        )
    
    def __str__(self):
        return f"user {self.user} to {self.store.name}"