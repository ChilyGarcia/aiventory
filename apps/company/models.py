from django.db import models
from apps.users.models import CustomUser


class Company(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='owned_companies'
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
