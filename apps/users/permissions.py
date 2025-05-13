from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from apps.company.models import Company
from apps.product.models import Product


def create_custom_permissions():
    # Get content types
    company_content_type = ContentType.objects.get_for_model(Company)
    product_content_type = ContentType.objects.get_for_model(Product)

    # Create permissions for Company
    company_permissions = [
        ("view_companies", "Can view companies"),
        ("create_company", "Can create company"),
        ("manage_employees", "Can manage company employees"),
        ("manage_company_users", "Can manage company users"),
    ]

    # Create permissions for Product
    product_permissions = [
        ("view_products", "Can view products"),
        ("create_product", "Can create product"),
        ("edit_product", "Can edit product"),
        ("delete_product", "Can delete product"),
    ]

    # Create all permissions
    for codename, name in company_permissions:
        Permission.objects.get_or_create(
            codename=codename, name=name, content_type=company_content_type
        )

    for codename, name in product_permissions:
        Permission.objects.get_or_create(
            codename=codename, name=name, content_type=product_content_type
        )
