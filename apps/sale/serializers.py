from rest_framework import serializers
from apps.sale.models import Sale


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"
        extra_kwargs = {"company": {"required": False}, "sold_by": {"required": False}}
