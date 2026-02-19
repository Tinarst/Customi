from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.filterset import FilterSet
import requests
import uuid
from account.models import Address
from cart.views import empty_cart
from order.serializers import OrderSerializer, OrderItemSerializer
from order.models import Order, OrderItem
from core.permissions import OrderItemSeller
from transaction.models import Payment
import logging

logger = logging.getLogger('customi')


class ZarinpallPayment:
    __ZARINPAL_URL_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    __callback_url = "http://127.0.0.1:8000/api/orders/payment_completion"
    __HEADER = {"Content-Type": "application/json", "Accept": "application/json"}

    def __init__(self, order: Order):
        self.merchant_id = uuid.uuid4()
        self.amount = order.total_amount
        self.description = "buy items from customy"
        self.order = order
        self.connect = False

    def request(self) -> bool:
        """if can connect to client server True else False"""
        if self.amount >= 200000000:
            print("Sandbox does not handle over 200M")
            return False
        if self.amount < 1000:
            print("Sandbox handle at least 1000")
            return False
        data = {
            "merchant_id": str(self.merchant_id),
            "amount": int(self.amount) * 10,
            "description": self.description,
            "callback_url": self.__callback_url,
        }

        response = requests.post(
            url=ZarinpallPayment.__ZARINPAL_URL_REQUEST,
            json=data,
            headers=ZarinpallPayment.__HEADER,
        )
        response_data = response.json()["data"]
        print(response.json())
        if response_data.get("message", None) == "Success":
            self.authority = response_data["authority"]
            self.code = response_data["code"]
            self.connect = True
            return True

        return False

    def payment(self):
        """if connection passed, return redirection url and create transaction object"""

        if self.connect:
            if not Payment.objects.filter(order=self.order).exists():

                transaction = Payment.objects.create(
                    authority=self.authority, order=self.order
                )
                logger.info("Transaction created; Pending")

            __URL = f"https://sandbox.zarinpal.com/pg/StartPay/{self.authority}"
            return __URL
        return False


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("user")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return self.request.user.order_user.exclude(orderitem_order__product_store=None)

    @action(methods=["POST"], detail=False)
    def checkout(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            order = serializer.save()
            payment = ZarinpallPayment(order)

        if payment.request():
            redirect_url = payment.payment()
            empty_cart(cart=request.user.cart_user)
            logger.info("Connected to Zarinpal server")
            return Response(
                status=status.HTTP_202_ACCEPTED, data={"payment_url": redirect_url}
            )
        logger.error("Error during connect to Zarinpal server")
        return Response(status=status.HTTP_502_BAD_GATEWAY)

    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def payment_completion(self, request: Request):
        """example: http://www.yoursite.ir/?Authority=A0000000000000000000000000000wwOGYpd&Status=OK"""

        authority = request.query_params.get("Authority")
        state = request.query_params.get("Status")
        transaction = get_object_or_404(Payment, authority=str(authority))
        order = transaction.order
        if state == "OK":
            order.status = order.OrderStatus.PAID
            transaction.status = transaction.PaymentStatus.PAID
            minus_stock_item(order)
            logger.info(f"Success payment for order id: {order.pk}")
            logger.info("PAID ORDER")
        else:
            order.status = order.OrderStatus.CANCELED
            transaction.status = transaction.PaymentStatus.CANCELED
            logger.info("CANCELED ORDER")
        order.save()
        transaction.save()
        OrderItem.objects.change_status(order)
        redirect_url = "http://localhost:5173/profile/orders"

        return redirect(redirect_url)

def minus_stock_item(order: Order):
    from stock.models import ProductStore
    order_items = order.orderitem_order.all()
    for item in order_items:
        item.product_store.stock -= item.quantity
        item.product_store.save()


class MyOrdersViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = OrderItem.objects.all()
    permission_classes = [OrderItemSeller]
    serializer_class = OrderItemSerializer
    
    def get_queryset(self):
        return OrderItem.objects.filter(product_store__store__seller=self.request.user)
    
    @action(methods=["POST"], detail=True)
    def change_status(self, request, pk=None):
        logger.info(f"Order {pk} status changed by user: {request.user}")
        return super().partial_update(request)