from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.filterset import FilterSet
import requests
import uuid
from account.models import Address
from cart.views import empty_cart
from order.serializers import OrderSerializer, OrderItemSerializer
from order.models import Order, OrderItem
from transaction.models import Payment


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
        return self.request.user.order_user.all()

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
            return Response(
                status=status.HTTP_202_ACCEPTED, data={"payment_url": redirect_url}
            )

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
        else:
            order.status = order.OrderStatus.CANCELED
            transaction.status = transaction.PaymentStatus.CANCELED
        order.save()
        transaction.save()
        redirect_url = "http://localhost:5173/profile/orders"

        return redirect(redirect_url)
