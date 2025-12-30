from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.viewsets import ModelViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, api_view
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import OTPCenter, CustomUser
from account.serializers import (
    OTPRegisterationSerializer,
    OTPloginSerializer,
    AccountSerializer
)
from source.settings import BASE_OTP_URL, AUTHORIZATION_OTP_API_KEY, PATTERN_CODE_OTP


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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        print(response.json())
        return response.json()["meta"]["status"]


class VerifyOTP(GenericAPIView):
    serializer_class = AccountSerializer

    def create_token(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return access_token, refresh_token

    def post(self, request, *args, **kwargs):
        print(request.data)
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
            "user": AccountSerializer(user).data
        }

        return Response(data, status=status.HTTP_200_OK)


class AccountViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = AccountSerializer
    
    
