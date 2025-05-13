from django.db import models
from django.core.validators import FileExtensionValidator
from apps.users.models import CustomUser


def company_logo_path(instance, filename):
    # El archivo se guardará en MEDIA_ROOT/company_logos/company_<id>/<filename>
    return f"company_logos/company_{instance.id}/{filename}"


class Company(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, related_name="owned_companies"
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    logo = models.ImageField(
        upload_to=company_logo_path,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
        help_text="Formato permitido: jpg, jpeg, png, webp. Tamaño máximo: 2MB",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Si es una instancia nueva, primero guardamos para obtener el ID
        if not self.pk and not self.logo:
            super().save(*args, **kwargs)
        super().save(*args, **kwargs)
