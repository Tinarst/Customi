from django.test import TestCase
from account.models import OTPCenter, CustomUser


class OTPCenterTestModel(TestCase):
    test_phone = "09122222222"

    def setUp(self):
        self.otp = OTPCenter.objects.create(self.test_phone)

    def test_active_otp(self):
        active_otp = OTPCenter.active(self.test_phone)

        self.assertEqual(self.otp, active_otp)

    def test_expired_otp(self):
        self.otp.created_at = self.otp.created_at - self.otp.expre_duration
        self.otp.save()

        self.assertFalse(OTPCenter.active(self.test_phone))

    def test_unique_otp(self):
        otp_finded_per_phone = OTPCenter.objects.filter(
            user_phone=self.test_phone, otp_code=self.otp.otp_code
        )
        self.assertEqual(len(otp_finded_per_phone), 1)


class CustomUserTestModel(TestCase):
    test_phone = "09122222222"

    def test_register_seller(self):
        user = CustomUser.objects.create(phone=self.test_phone, userType=True)
        
        self.assertEqual(user.role, user.UserRole.SELLER)

    def test_register_customer(self):
        user = CustomUser.objects.create(phone=self.test_phone, userType=False)
        
        self.assertEqual(user.role, user.UserRole.CUSTOMER)
    
    def test_create_with_normalize_phone(self):
        user = CustomUser.objects.create(phone="9122222222")
        
        self.assertEqual(user.phone, self.test_phone)
    
    def test_seller_with_no_store(self):
        user = CustomUser.objects.create(phone=self.test_phone)
        
        self.assertFalse(user.is_seller)