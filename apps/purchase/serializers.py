from rest_framework import serializers
from apps.purchase.models import Purchase


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = "__all__"
        extra_kwargs = {
            'company': {'required': False},
            'total_cost': {'required': False}
        }
