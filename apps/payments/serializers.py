from rest_framework import serializers
from .models import WompiTransaction
from apps.subscription.models import Subscription


class WompiTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WompiTransaction
        fields = ['id', 'subscription', 'amount', 'currency', 'payment_method_type']
        read_only_fields = ['transaction_id', 'reference', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Simular la creación de una transacción exitosa
        transaction = WompiTransaction.objects.create(
            **validated_data,
            status='APPROVED',
            transaction_id=f'sim_{validated_data["subscription"].id}_{validated_data["amount"]}',
            reference=f'ref_{validated_data["subscription"].id}_{validated_data["amount"]}',
            amount_in_cents=int(float(validated_data["amount"]) * 100)
        )

        # Activar la suscripción
        subscription = transaction.subscription
        subscription.is_active = True
        subscription.save()

        return transaction
