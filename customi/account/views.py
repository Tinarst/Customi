from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, api_view
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import OTPCenter, CustomUser, Address
from account.serializers import (
    OTPRegisterationSerializer,
    OTPloginSerializer,
    AccountSerializer,
    AddressSerializer,
)
from source.settings import BASE_OTP_URL, AUTHORIZATION_OTP_API_KEY, PATTERN_CODE_OTP
import logging

logger = logging.getLogger('customi')



def get_user_or_404(phone):
    phone = CustomUser.normalize_phone(phone)
    user = get_object_or_404(CustomUser, phone=phone)
    return user


class RequestOTP(GenericAPIView):
    queryset = OTPCenter.objects.all()

    def get_serializer_class(self):
        if self.request.data.get("userType", None) is None:
            return OTPloginSerializer
        return OTPRegisterationSerializer

    def create(self):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            return serializer.save()

    def request_otp(self):
        otp = self.create()
        code = otp.otp_code
        phone = otp.user_phone
        return self.send_otp(code, phone)

    def post(self, request, *args, **kwargs):
        response = self.request_otp()
        serializer = self.get_serializer()
        if response:
            logger.info("OTP sent successfully")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error("Error during connect to OTP server")
        return Response(serializer.data, status=status.HTTP_409_CONFLICT)

    def send_otp(self, otp, phone):
        payload = {
            "sending_type": "pattern",
            "from_number": "+983000505",
            "code": PATTERN_CODE_OTP,
            "recipients": [f"{phone}"],
            "params": {"code": f"{otp}"},
            "phonebook": {
                "id": 1,
                "name": None,
                "pre": None,
                "email": "",
                "options": "",
            },
        }
        header = {
            "Authorization": AUTHORIZATION_OTP_API_KEY,
            "Content-Type": "application/json",
        }
        response = requests.post(url=BASE_OTP_URL, headers=header, json=payload)
        return response.json()["meta"]["status"]


class VerifyOTP(GenericAPIView):
    serializer_class = AccountSerializer

    def create_token(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return access_token, refresh_token

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get("username")
        otp = int(self.request.data.get("password"))
        otp_object = get_object_or_404(
            OTPCenter,
            user_phone=phone,
            otp_code=otp,
        )
        user = get_user_or_404(phone)
        access_token, refresh_token = self.create_token(user)
        otp_object.delete()
        data = {
            "access": str(access_token),
            "refresh": str(refresh_token),
            "user": AccountSerializer(user).data,
        }
        logger.info("User entered successfully")

        return Response(data, status=status.HTTP_200_OK)


class AccountView(GenericAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = AccountSerializer
    model = get_user_model()

    def __retrieve_user(self):
        if self.request.user and self.request.user.is_authenticated:
            return self.request.user
        return None

    def get(self, request, *args, **kwargs):
        user = self.__retrieve_user()
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        
        user = self.__retrieve_user()
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        logger.info("User changed information")
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateAddressMixin:
    def create(self, request, *args, **kwargs):
        context = {"user": request.user}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddressViewSet(CreateAddressMixin, ModelViewSet):
    queryset = Address.objects.select_related("user")
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        queryset = user.address_user.all()
        return queryset

    def update(self, request, *args, **kwargs):
        self.kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
