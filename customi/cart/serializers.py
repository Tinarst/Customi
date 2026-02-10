from rest_framework import serializers
from cart.models import CartItem, Cart
from stock.serializers import (
    ProductStoreSerializer,
    StoreSerializer,
    ProductImageSerializer,
)
from stock.models import Product


class ProductCartSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(source="productimage_product", many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "images"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer(source="product_store.product")
    store = StoreSerializer(source="product_store.store")
    store_item = ProductStoreSerializer(source="product_store")
    unit_price = serializers.FloatField(source="product_store.price")
    unit_discount = serializers.FloatField(source="product_store.discount_price")
    total_price = serializers.FloatField()
    total_discount = serializers.FloatField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "store",
            "store_item",
            "total_discount",
            "total_price",
            "unit_discount",
            "unit_price",
            "quantity",
        ]
        read_only_fields = [
            "unit_price",
            "unit_discount",
            "total_price",
            "total_discount",
            "store",
            "store_item",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cartitem_cart", many=True)
    total_price = serializers.FloatField(read_only=True)
    total_discount = serializers.FloatField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_discount"]
