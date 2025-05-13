from rest_framework import serializers
from .models import Subscription
from apps.plan.models import Plan
from datetime import datetime, timedelta


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active']
        read_only_fields = ['is_active', 'end_date']
        extra_kwargs = {
            'start_date': {'read_only': True},
        }

    def create(self, validated_data):
        # Establecer fecha de inicio como ahora
        validated_data['start_date'] = datetime.now()
        # Calcular fecha de fin (1 mes después)
        validated_data['end_date'] = validated_data['start_date'] + timedelta(days=30)
        # Suscripción inactiva hasta que se procese el pago
        validated_data['is_active'] = False
        return super().create(validated_data)
