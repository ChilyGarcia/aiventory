from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import uuid
from .models import WompiTransaction
from apps.subscription.models import Subscription


class WompiTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WompiTransaction
        fields = ["id", "subscription", "payment_method_type"]
        read_only_fields = [
            "transaction_id",
            "reference",
            "status",
            "created_at",
            "updated_at",
            "amount",
            "amount_in_cents",
            "currency",
        ]

    def validate_subscription(self, subscription):
        # Verificar si la suscripción ya está activa
        if subscription.is_active:
            raise ValidationError(
                "Esta suscripción ya está activa. No se pueden procesar más pagos para ella."
            )
        return subscription

    def create(self, validated_data):
        subscription = validated_data["subscription"]
        plan_price = subscription.plan.price

        # Generar IDs únicos usando timestamp y uuid
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]

        # Simular la creación de una transacción exitosa
        transaction = WompiTransaction.objects.create(
            **validated_data,
            status="APPROVED",
            amount=plan_price,
            amount_in_cents=int(float(plan_price) * 100),
            currency="COP",
            transaction_id=f"sim_{subscription.id}_{timestamp}_{unique_id}",
            reference=f"ref_{subscription.id}_{timestamp}_{unique_id}",
        )

        # Activar la suscripción
        subscription.is_active = True
        subscription.save()

        return transaction
