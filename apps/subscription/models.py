from django.db import models
from apps.users.models import CustomUser
from apps.plan.models import Plan


class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"
