from rest_framework import serializers
from account.models import CustomUser, OTPCenter, Address


class UsernameValidateSerializerMixin:
    def validate_username(self, value):
        if len(value) not in (10, 11, 13) or not value.isdigit():
            print("Invalid phone number")
            raise serializers.ValidationError("Invalid phone number")
        return value


class BaseOTPSerializer(serializers.Serializer, UsernameValidateSerializerMixin):
    username = serializers.CharField()
    password = serializers.CharField(required=False)

    def validate(self, validated_data: dict):
        user_phone = validated_data.get("username")
        if OTPCenter.active(user_phone) and not validated_data.get("password", None):
            print("OTP has been sended")
            raise serializers.ValidationError("OTP has been sended")
        return validated_data

    def create(self, validated_data: dict):
        """Return otp obj"""

        user_phone = validated_data.get("username")
        otp = OTPCenter.objects.create(user_phone)
        return otp


class OTPRegisterationSerializer(BaseOTPSerializer):
    """Use for register otp request"""

    userType = serializers.BooleanField()

    def validate_username(self, value: str):
        if CustomUser.objects.filter(phone__icontains=value[-10:]).exists():
            print("Phone number is already exist")
            raise serializers.ValidationError("Phone number is already exist")

        return super().validate_username(value)

    def create(self, validated_data: dict):
        """Create user and otp; return otp object"""

        user_phone = validated_data.get("username")
        userType = validated_data.get("userType")
        CustomUser.objects.create(user_phone, userType)
        return super().create(validated_data)


class OTPloginSerializer(BaseOTPSerializer):
    """Use for login otp request"""

    def validate_username(self, value: str):
        if not CustomUser.objects.filter(phone__icontains=value[-10:]).exists():
            print("Phone number does not exist")
            raise serializers.ValidationError("Phone number does not exist")

        return value


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "country",
            "city",
            "state",
            "address_line_1",
            "address_line_2",
            "postal_code",
            "created_at",
            "updated_at",
        ]

    def validate_postal_code(self, value: str):
        if value:
            if (
                self.Meta.model.objects.filter(postal_code=value).exists()
                and value != self.instance.postal_code
            ):
                print("Postal code already exist")
                raise serializers.ValidationError("Postal code already exist")
            if not value.isdigit() or not len(value) != 10:
                print("Invalid postal code")
                raise serializers.ValidationError("Invalid postal code")
            return value
        return None

    def create(self, validated_data):
        user = self.context.get("user", None)
        if not user:
            raise serializers.ValidationError("user not found")
        address = self.Meta.model(**validated_data)
        address.user = user
        address.save()
        return address


class AccountSerializer(serializers.ModelSerializer, UsernameValidateSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    status = serializers.BooleanField(source="is_active", read_only=True)
    is_seller = serializers.BooleanField(read_only=True)
    address = AddressSerializer(source="address_user", many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "status",
            "is_seller",
            "email",
            "phone",
            "first_name",
            "last_name",
            "picture",
            "address",
        ]

    def validate_phone(self, value):
        value = super().validate_username(value)
        if (
            CustomUser.objects.filter(phone__icontains=value[-10:]).exists()
            and value != self.instance.phone
        ):
            print("Phone number is already exist")
            raise serializers.ValidationError("Phone number is already exist")
        return value

    def validate_email(self, value):
        if not value:
            return None
        value = value.lower()
        if (
            CustomUser.objects.filter(email=value.lower()).exists()
            and value != self.instance.email
        ):
            print("email is already exist")
            raise serializers.ValidationError("Email number is already exist")
        return value
