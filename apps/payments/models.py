from django.db import models
from apps.subscription.models import Subscription


class WompiTransaction(models.Model):
    TRANSACTION_STATUS = (('PENDING', 'Pendiente'), ('APPROVED', 'Aprobada'),
                          ('DECLINED', 'Declinada'), ('VOIDED', 'Anulada'),
                          ('ERROR', 'Error'))

    subscription = models.ForeignKey(Subscription,
                                     on_delete=models.CASCADE,
                                     related_name='wompi_transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount_in_cents = models.IntegerField()
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    status = models.CharField(max_length=20,
                              choices=TRANSACTION_STATUS,
                              default='PENDING')
    payment_method_type = models.CharField(max_length=50)
    payment_method_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wompi_response = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
