from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role


@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    if sender.name == "users":
        # Crear rol de emprendedor si no existe
        Role.objects.get_or_create(
            name=Role.ENTREPRENEUR,
        )

        # Crear rol de empleado si no existe
        Role.objects.get_or_create(
            name=Role.EMPLOYEE,
        )
