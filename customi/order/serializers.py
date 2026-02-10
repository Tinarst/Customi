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
    total_price = serializers.CharField()
    store_item = ProductStoreSerializer(source="product_store", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "total_price",
            "price",
            "quantity",
            "store_item",
        ]


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


# {
#     "count": int,
#     "results":
#         [
#             {
#                 "address":
#                     {
#                         "created_at": "<dateTime>",
#                         "id": "<integer>",
#                         "updated_at": "<dateTime>",
#                         "label": "<string>",
#                         "address_line_1": "<string>",
#                         "address_line_2": "<string>",
#                         "city": "<string>",
#                         "state": "<string>",
#                         "postal_code": "<string>",
#                         "country": "<string>"
#                     },

#                 "created_at": "<dateTime>",
#                 "id": "<integer>",
#                 "items":
#                     [
#                         {
#                             "id": "<integer>",
#                             "price": "56809127",
#                             "store_item":
#                                 {
#                                     "created_at": "<dateTime>",
#                                     "id": "<integer>",
#                                     "price": "628992058748861.",

#                                     "product": {
#                                         "categories": [
#                                             {
#                                                 "detail_url": "<uri>",
#                                                 "id": "<integer>",
#                                                 "name": "<string>",
#                                                 "description": "<string>",
#                                                 "image": "<uri>",
#                                                 "is_active": "<boolean>"
#                                             },
#                                         ],

#                                         "description": "<string>",
#                                         "id": "<integer>",
#                                         "name": "<string>",
#                                         "rating": "<string>",
#                                         "images": [
#                                             {"id": "<integer>","image": "<uri>"},
#                                         ]
#                                     },
#                                     "stock": "<long>",
#                                     "store": {
#                                         "description": "<string>",
#                                         "id": "<integer>",
#                                         "name": "<string>",
#                                         "seller": "<uri>"
#                                         },
#                                     "updated_at": "<dateTime>",
#                                     "discount_price": ".",
#                                     "is_active": "<boolean>"
#                                 }
#                             "total_price": "78958.99",
#                             "status": 3,
#                             "quantity": "<long>"
#                         },
#                     ],
#                 "payment":
#                     {
#                         "amount": "-87.41",
#                         "created_at": "<dateTime>",
#                         "id": "<integer>",
#                         "order": "<integer>",
#                         "payment_url": "<string>",
#                         "status": "<string>",
#                         "updated_at": "<dateTime>",
#                         "transaction_id": "<string>",
#                         "reference_id": "<string>",
#                         "card_pan": "<string>",
#                         "fee": "<string>"
#                     },
#                 "total_price": "7",
#                 "updated_at": "<dateTime>"
#                 "status": 3
#             }
#         ]
#     }
