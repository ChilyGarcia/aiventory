from django.db import models
from apps.company.models import Company


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("export_supplier", "Can export supplier data"),
            ("import_supplier", "Can import supplier data"),
        ]
