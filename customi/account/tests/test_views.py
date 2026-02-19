from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from account.models import OTPCenter, CustomUser


class OTPCenterViewTest(APITestCase):
    test_phone = test_phone = "09123456789"

    def entery_cycle(self, custom_phone=None, userType=None):
        username = custom_phone if custom_phone else self.test_phone
        path = reverse("request-otp")
        if userType is not None:
            data = {"username": username, "userType": userType}
        else:
            data = {"username": username}

        response = self.client.post(data=data, path=path)

        return response

    def test_user_creation_with_otp(self):
        """Send and create otp code & user with userType with valid phone"""

        response = self.entery_cycle(userType=True)

        user = CustomUser.objects.filter(phone=self.test_phone)
        otp = OTPCenter.objects.filter(user_phone=self.test_phone)

        self.assertTrue(user.exists())
        self.assertTrue(otp.exists())
        self.assertEqual(response.status_code, 200)

    def test_otp_creation_with_existance_user(self):
        """Sending otp code with user without userType value"""
        # login
        CustomUser.objects.create(self.test_phone)

        response = self.entery_cycle()

        otp = OTPCenter.objects.filter(user_phone=self.test_phone)

        self.assertTrue(otp.exists())
        self.assertEqual(response.status_code, 200)

    def test_resend_otp_with_available_otp(self):
        OTPCenter.objects.create(self.test_phone)
        CustomUser.objects.create(self.test_phone)
        response = self.entery_cycle()

        self.assertTrue(response.status_code, 400)

    def test_not_create_user_with_exist_phone(self):
        """Not creating otp code & user for exist user with userType value"""
        # login

        CustomUser.objects.create(self.test_phone)
        response = self.entery_cycle(userType=False)
        otp = OTPCenter.objects.filter(user_phone=self.test_phone)

        self.assertFalse(otp.exists())
        self.assertEqual(response.status_code, 400)

    def test_not_create_user_with_unnormal_phone(self):
        """Test for matching values of the same phone number and not create otp"""
        # login
        CustomUser.objects.create(self.test_phone)
        response = self.entery_cycle(custom_phone="+989123456789", userType=False)
        response2 = self.entery_cycle(custom_phone="9123456789", userType=False)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)

    def test_enter_with_invalid_phone(self):
        # login, register
        response = self.entery_cycle(
            custom_phone="+98912345678", userType=False
        )  # length
        response2 = self.entery_cycle(
            custom_phone="+9891p2345678", userType=False
        )  # string

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)


class VerifyOTPViewTest(APITestCase):
    test_phone = "09123456789"

    def test_verify_otp_cycle(self):
        data = {"username": self.test_phone, "userType": False}

        url = reverse("request-otp")
        self.client.post(data=data, path=url)
        otp = OTPCenter.objects.get(user_phone=self.test_phone)
        url = reverse("verify-otp")
        data = {"username": self.test_phone, "password": otp.otp_code}
        response = self.client.post(data=data, path=url)

        self.assertTrue(response.status_code, 200)
