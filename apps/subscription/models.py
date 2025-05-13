from django.db import models
from django.utils import timezone
from apps.users.models import CustomUser
from apps.plan.models import Plan


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        status = "Activa" if self.is_active else "Inactiva"
        return f"{self.user} - {self.plan} ({status})"

    def is_expired(self):
        return timezone.now() > self.end_date

    def save(self, *args, **kwargs):
        # Si esta suscripción se está activando
        if self.is_active:
            # Desactivar todas las otras suscripciones del usuario
            Subscription.objects.filter(user=self.user).exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)
