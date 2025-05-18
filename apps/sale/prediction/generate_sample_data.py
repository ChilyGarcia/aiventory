import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
import sys

# Configurar entorno Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.sale.models import Sale
from apps.product.models import Product
from apps.company.models import Company
from apps.users.models import CustomUser


def list_companies_and_users():
    """Lista todas las compañías y usuarios disponibles"""
    print("\n=== COMPAÑÍAS DISPONIBLES ===")
    companies = Company.objects.all()
    if not companies:
        print("No hay compañías registradas en el sistema.")
    else:
        for company in companies:
            products_count = Product.objects.filter(company=company).count()
            print(f"ID: {company.id} | Nombre: {company.name} | Productos: {products_count}")
    
    print("\n=== USUARIOS DISPONIBLES ===")
    users = CustomUser.objects.all()
    if not users:
        print("No hay usuarios registrados en el sistema.")
    else:
        for user in users:
            print(f"ID: {user.id} | Nombre: {user.first_name} {user.last_name} | Email: {user.email}")

def generate_sample_sales(
    company_id, user_id, days=30, min_sales_per_day=1, max_sales_per_day=5
):
    """Genera datos de ventas de muestra para entrenar el modelo de predicción"""
    print(f"\n=== GENERANDO DATOS DE PRUEBA ===")
    print(f"Compañía ID: {company_id} | Usuario ID: {user_id}")
    print(f"Período: últimos {days} días | Ventas por día: {min_sales_per_day}-{max_sales_per_day}")
    
    try:
        # Obtener compañía
        try:
            company = Company.objects.get(id=company_id)
            print(f"Compañía encontrada: {company.name}")
        except Company.DoesNotExist:
            print(f"ERROR: No existe una compañía con ID {company_id}")
            return False
            
        # Obtener usuario
        try:
            user = CustomUser.objects.get(id=user_id)
            print(f"Usuario encontrado: {user.first_name} {user.last_name}")
        except CustomUser.DoesNotExist:
            print(f"ERROR: No existe un usuario con ID {user_id}")
            return False

        # Verificar productos
        products = Product.objects.filter(company=company)
        if not products:
            print(f"ERROR: No hay productos para la compañía {company.name}")
            return False
        else:
            print(f"Productos disponibles: {products.count()}")

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

        print("\n=== RESULTADOS ===")
        print(
            f"Se generaron {sales_count} ventas de prueba para los últimos {days} días"
        )
        print("Las ventas han sido creadas exitosamente en la base de datos.")
        print("Ahora puedes usar el endpoint de predicción de ventas.")
        return True

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n=== GENERADOR DE DATOS DE PRUEBA PARA PREDICCIÓN DE VENTAS ===")
    
    # Si se pasan argumentos, usar esos valores
    if len(sys.argv) >= 3:
        try:
            company_id = int(sys.argv[1])
            user_id = int(sys.argv[2])
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            min_sales = int(sys.argv[4]) if len(sys.argv) > 4 else 1
            max_sales = int(sys.argv[5]) if len(sys.argv) > 5 else 5
            
            generate_sample_sales(
                company_id=company_id,
                user_id=user_id,
                days=days,
                min_sales_per_day=min_sales,
                max_sales_per_day=max_sales,
            )
        except ValueError:
            print("Error: Los argumentos deben ser números enteros.")
            print("Uso: python generate_sample_data.py [company_id] [user_id] [days] [min_sales] [max_sales]")
    else:
        # Si no hay argumentos, mostrar compañías y usuarios disponibles
        list_companies_and_users()
        
        print("\n=== INSTRUCCIONES ===")
        print("Para generar datos de prueba, ejecuta este script con los parámetros adecuados:")
        print("python manage.py shell -c \"exec(open('apps/sale/prediction/generate_sample_data.py').read())\" [company_id] [user_id]")
        print("\nEjemplo:")
        print("python manage.py shell -c \"exec(open('apps/sale/prediction/generate_sample_data.py').read())\" 2 1")
        
        # Preguntar al usuario si quiere usar valores predeterminados
        print("\n¿Deseas usar los valores predeterminados? (COMPANY_ID=2, USER_ID=2, days=30)")
        response = input("Escribe 'si' para continuar, cualquier otra cosa para salir: ")
        
        if response.lower() == 'si':
            generate_sample_sales(
                company_id=2,
                user_id=2,
                days=30,
                min_sales_per_day=1,
                max_sales_per_day=5,
            )
