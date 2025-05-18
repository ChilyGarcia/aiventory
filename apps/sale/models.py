from django.db import models
from apps.company.models import Company
from apps.product.models import Product
from apps.users.models import CustomUser


class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField()
    sold_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.product.stock = models.F("stock") - self.quantity
        self.product.save(update_fields=["stock"])
