from django.core.management.base import BaseCommand, CommandError
from apps.company.models import Company
from apps.product.models import Product
from apps.sale.models import Sale
from apps.users.models import CustomUser
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = "Genera datos de ventas de prueba para entrenar el modelo de predicción de ventas"

    def add_arguments(self, parser):
        parser.add_argument("--company", type=int, help="ID de la compañía")
        parser.add_argument(
            "--user", type=int, help="ID del usuario que realiza las ventas"
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Número de días hacia atrás para generar datos",
        )
        parser.add_argument(
            "--min", type=int, default=1, help="Mínimo de ventas por día"
        )
        parser.add_argument(
            "--max", type=int, default=5, help="Máximo de ventas por día"
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="Listar compañías y usuarios disponibles",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self.list_companies_and_users()
            return

        if not options["company"] or not options["user"]:
            self.stderr.write(
                self.style.ERROR(
                    "Error: Debes proporcionar los IDs de compañía y usuario"
                )
            )
            self.stdout.write(
                "Para ver compañías y usuarios disponibles, usa: python manage.py generate_sales_data --list"
            )
            return

        company_id = options["company"]
        user_id = options["user"]
        days = options["days"]
        min_sales = options["min"]
        max_sales = options["max"]

        self.generate_sales_data(company_id, user_id, days, min_sales, max_sales)

    def list_companies_and_users(self):
        self.stdout.write(self.style.SUCCESS("\n=== COMPAÑÍAS DISPONIBLES ==="))
        companies = Company.objects.all()
        if not companies:
            self.stdout.write(
                self.style.WARNING("No hay compañías registradas en el sistema.")
            )
        else:
            for company in companies:
                products_count = Product.objects.filter(company=company).count()
                self.stdout.write(
                    f"ID: {company.id} | Nombre: {company.name} | Productos: {products_count}"
                )

        self.stdout.write(self.style.SUCCESS("\n=== USUARIOS DISPONIBLES ==="))
        users = CustomUser.objects.all()
        if not users:
            self.stdout.write(
                self.style.WARNING("No hay usuarios registrados en el sistema.")
            )
        else:
            for user in users:
                self.stdout.write(
                    f"ID: {user.id} | Nombre: {user.first_name} {user.last_name} | Email: {user.email}"
                )

    def generate_sales_data(
        self, company_id, user_id, days, min_sales_per_day, max_sales_per_day
    ):
        self.stdout.write(self.style.SUCCESS("\n=== GENERANDO DATOS DE PRUEBA ==="))
        self.stdout.write(f"Compañía ID: {company_id} | Usuario ID: {user_id}")
        self.stdout.write(
            f"Período: últimos {days} días | Ventas por día: {min_sales_per_day}-{max_sales_per_day}"
        )

        try:
            try:
                company = Company.objects.get(id=company_id)
                self.stdout.write(
                    self.style.SUCCESS(f"Compañía encontrada: {company.name}")
                )
            except Company.DoesNotExist:
                raise CommandError(f"No existe una compañía con ID {company_id}")

            try:
                user = CustomUser.objects.get(id=user_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Usuario encontrado: {user.first_name} {user.last_name}"
                    )
                )
            except CustomUser.DoesNotExist:
                raise CommandError(f"No existe un usuario con ID {user_id}")

            products = Product.objects.filter(company=company)
            if not products:
                raise CommandError(f"No hay productos para la compañía {company.name}")
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Productos disponibles: {products.count()}")
                )

            current_date = datetime.now()
            sales_count = 0

            for day in range(days):
                sale_date = current_date - timedelta(days=day)

                num_sales = random.randint(min_sales_per_day, max_sales_per_day)

                for _ in range(num_sales):
                    product = random.choice(products)
                    quantity = random.randint(1, 10)
                    Sale.objects.create(
                        company=company,
                        product=product,
                        customer=f"Cliente de prueba {random.randint(1, 100)}",
                        quantity=quantity,
                        unit_price=product.price,
                        total_price=Decimal(quantity) * product.price,
                        date=sale_date,
                        sold_by=user,
                    )

                    sales_count += 1

                if day % 5 == 0 or day == days - 1:
                    self.stdout.write(f"Progreso: {day + 1}/{days} días procesados...")

            self.stdout.write(self.style.SUCCESS("\n=== RESULTADOS ==="))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Se generaron {sales_count} ventas de prueba para los últimos {days} días"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Las ventas han sido creadas exitosamente en la base de datos."
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Ahora puedes usar el endpoint de predicción de ventas."
                )
            )

        except Exception as e:
            raise CommandError(f"Error al generar datos de prueba: {str(e)}")
