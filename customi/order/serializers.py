from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Order, OrderItem
from account.serializers import AddressSerializer
from account.models import Address
from transaction.serializers import PaymentSerializer
from stock.serializers import ProductSerializer, StoreSerializer
from stock.models import ProductStore


class ProductStoreSerializer(serializers.ModelSerializer):
  product = ProductSerializer()
  store = StoreSerializer()

  class Meta:
    model = ProductStore
    fields = [
        "id",
        "created_at",
        "updated_at",
        "price",
        "discount_price",
        "store",
        "stock",
        "product",
    ]


class OrderItemSerializer(serializers.ModelSerializer):
  total_price = serializers.CharField(source="price")
  store_item = ProductStoreSerializer(source="product_store")
  user = serializers.SerializerMethodField()

  class Meta:
    model = OrderItem
    fields = [
        "id",
        "total_price",
        "price",
        "quantity",
        "store_item",
        "user",
        "status",
    ]
    read_only_fields = [
        "id",
        "price",
        "total_price",
        "quantity",
        "store_item",
        "user",
    ]

  def get_user(self, order_item: OrderItem):
    user = {
        "first_name": order_item.order.user.first_name,
        "last_name": order_item.order.user.last_name,
    }
    return user
  
  def update(self, instance, validated_data):
    order_items = OrderItem.objects.filter(order=instance.order)
    status = validated_data.get("status", None)
    order_item = super().update(instance, validated_data)

    if all(item.status == status for item in order_items):
      instance.order.status = status
      instance.order.save()
    return order_item

class OrderSerializer(serializers.ModelSerializer):
  address = AddressSerializer(source="shipping_address", read_only=True)
  address_id = serializers.PrimaryKeyRelatedField(
      queryset=Address.objects.select_related("user"),
      source="shipping_address",
      required=False,
      write_only=True,
  )
  total_price = serializers.CharField(source="total_amount", read_only=True)
  payment = PaymentSerializer(source="payment_order", read_only=True)
  items = OrderItemSerializer(
      source="orderitem_order", many=True, required=False, read_only=True
  )
  status = serializers.IntegerField(read_only=True)

  class Meta:
    model = Order
    fields = [
        "id",
        "created_at",
        "updated_at",
        "address",
        "address_id",
        "items",
        "payment",
        "total_price",
        "status",
    ]

  def create(self, validated_data):
    return Order.objects.create(
        user=self.context.get("user"),
        shipping_address=validated_data["shipping_address"],
    )

  def update(self, instance, validated_data):

      return super().update(instance, validated_data)

