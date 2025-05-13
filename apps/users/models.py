from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    ENTREPRENEUR = "entrepreneur"
    EMPLOYEE = "employee"

    ROLE_CHOICES = [
        (ENTREPRENEUR, "Entrepreneur"),
        (EMPLOYEE, "Employee"),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def has_permission(self, permission_name):
        return self.permissions.filter(codename=permission_name).exists()

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    document_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    custom_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_permissions",
        help_text="Specific permissions for this user.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def has_custom_permission(self, permission_name):
        # Verificar si el usuario tiene el permiso directamente
        if self.custom_permissions.filter(codename=permission_name).exists():
            return True

        # Si no tiene el permiso directamente y no tiene rol, no tiene el permiso
        if not self.role:
            return False

        # Verificar si el rol tiene el permiso
        return self.role.has_permission(permission_name)

    def __str__(self):
        return self.email
