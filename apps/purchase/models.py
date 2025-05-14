from django.db import models
from apps.company.models import Company
from apps.product.models import Product


class Purchase(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
        self.product.stock = models.F("stock") + self.quantity
        self.product.save(update_fields=["stock"])
