from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from apps.users.models import Role


class Command(BaseCommand):
    help = "Create initial permissions and content types"

    def handle(self, *args, **kwargs):
        # Crear content types
        company_content_type, _ = ContentType.objects.get_or_create(
            app_label="company", model="company"
        )
        product_content_type, _ = ContentType.objects.get_or_create(
            app_label="product", model="product"
        )
        sale_content_type, _ = ContentType.objects.get_or_create(
            app_label="sale", model="sale"
        )
        purchase_content_type, _ = ContentType.objects.get_or_create(
            app_label="purchase", model="purchase"
        )

        # Crear permisos
        permissions_data = [
            {
                "name": "Can create company",
                "codename": "create_company",
                "content_type": company_content_type,
            },
            {
                "name": "Can manage company users",
                "codename": "manage_company_users",
                "content_type": company_content_type,
            },
            {
                "name": "Can view companies",
                "codename": "view_companies",
                "content_type": company_content_type,
            },
            {
                "name": "Can manage employees",
                "codename": "manage_employees",
                "content_type": company_content_type,
            },
            {
                "name": "Can view products",
                "codename": "view_products",
                "content_type": product_content_type,
            },
            {
                "name": "Can create product",
                "codename": "create_product",
                "content_type": product_content_type,
            },
            {
                "name": "Can view sales",
                "codename": "view_sales",
                "content_type": sale_content_type,
            },
            {
                "name": "Can create sale",
                "codename": "create_sale",
                "content_type": sale_content_type,
            },
            {
                "name": "Can edit sale",
                "codename": "edit_sale",
                "content_type": sale_content_type,
            },
            {
                "name": "Can delete sale",
                "codename": "delete_sale",
                "content_type": sale_content_type,
            },
            {
                "name": "Can view purchases",
                "codename": "view_purchases",
                "content_type": purchase_content_type,
            },
            {
                "name": "Can create purchase",
                "codename": "create_purchase",
                "content_type": purchase_content_type,
            },
            {
                "name": "Can edit purchase",
                "codename": "edit_purchase",
                "content_type": purchase_content_type,
            },
            {
                "name": "Can delete purchase",
                "codename": "delete_purchase",
                "content_type": purchase_content_type,
            },
            {
                "name": "Can edit product",
                "codename": "edit_product",
                "content_type": product_content_type,
            },
            {
                "name": "Can delete product",
                "codename": "delete_product",
                "content_type": product_content_type,
            },
        ]

        created_permissions = []
        for perm_data in permissions_data:
            permission, _ = Permission.objects.get_or_create(
                name=perm_data["name"],
                codename=perm_data["codename"],
                content_type=perm_data["content_type"],
            )
            created_permissions.append(permission)

        # Crear roles
        entrepreneur_role, _ = Role.objects.get_or_create(name="entrepreneur")
        employee_role, _ = Role.objects.get_or_create(name="employee")

        # Asignar permisos a roles
        entrepreneur_role.permissions.set(created_permissions)
        employee_role.permissions.set(
            [
                p
                for p in created_permissions
                if p.codename in ["view_companies", "view_products"]
            ]
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully created permissions and roles")
        )
