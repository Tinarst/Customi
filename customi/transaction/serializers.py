from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.CharField(source="order.total_amount")
    
    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "status",
            "order",
            "created_at",
            "updated_at"
        ]