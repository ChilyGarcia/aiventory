from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from apps.product.services.product_service import ProductService
from apps.product.serializers import ProductSerializer
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from apps.sale.models import Sale
from apps.purchase.models import Purchase
from datetime import datetime


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
        self.company_service = CompanyService()

    @custom_permission_required("view_products")
    def list(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener productos de todas las compañías del usuario
            all_products = []
            for company in companies:
                products = self.service.get_all_by_company(company)
                all_products.extend(products)

            serializer = ProductSerializer(all_products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @custom_permission_required("view_products")
    def retrieve(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = self.service.get_by_id(pk)
            if not product:
                return Response(
                    {"error": "Producto no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if product.company not in companies:
                return Response(
                    {"error": "No tienes permiso para ver este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required("create_product")
    def create(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            company = companies[0]

            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                product = serializer.save(company=company)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @custom_permission_required("edit_product")
    def update(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = self.service.get_by_id(pk)
            if not product:
                return Response(
                    {"error": "Producto no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if product.company not in companies:
                return Response(
                    {
                        "error":
                        "No tienes permiso para actualizar este producto"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                updated_product = serializer.save(company=product.company)
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required("delete_product")
    def destroy(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = self.service.get_by_id(pk)
            if not product:
                return Response(
                    {"error": "Producto no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Verificar que el producto pertenece a una de las compañías del usuario
            if product.company not in companies:
                return Response(
                    {"error": "No tienes permiso para eliminar este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="statistics", url_name="product-statistics")
    @custom_permission_required("view_products")
    def statistics(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Estadísticas para todas las compañías del usuario
            stats = {
                "total_products": 0,  # Cantidad de productos diferentes
                "total_stock": 0,    # Suma total de todas las unidades en stock
                "low_stock": 0,      # Suma de unidades con stock bajo
                "out_of_stock": 0    # Cantidad de productos agotados
            }

            # Definir un umbral para el stock bajo (menos de 5 unidades)
            LOW_STOCK_THRESHOLD = 5

            for company in companies:
                products = self.service.get_all_by_company(company)

                # Total de productos diferentes
                stats["total_products"] += len(products)

                # Suma total de todas las unidades en stock
                total_stock = sum(p.stock for p in products)
                stats["total_stock"] += total_stock

                # Suma de unidades con stock bajo
                low_stock_units = sum(p.stock for p in products 
                                    if 0 < p.stock < LOW_STOCK_THRESHOLD)
                stats["low_stock"] += low_stock_units

                # Cantidad de productos agotados
                out_of_stock = sum(1 for p in products if p.stock == 0)
                stats["out_of_stock"] += out_of_stock

            return Response(stats)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="monthly-flow")
    @custom_permission_required("view_products")
    def monthly_inventory_flow(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Año para el que queremos obtener los datos (por defecto el año actual)
            year = request.query_params.get('year', datetime.now().year)
            try:
                year = int(year)
            except ValueError:
                year = datetime.now().year
            
            # Diccionario para almacenar los datos de cada mes
            monthly_data = []
            
            # Nombres abreviados de los meses en español
            month_names = {
                1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
            }
            
            # Obtener las ventas y compras del año especificado para las compañías del usuario
            sales = Sale.objects.filter(
                company__in=companies,
                date__year=year
            )
            
            purchases = Purchase.objects.filter(
                company__in=companies,
                date__year=year
            )
            
            # Datos mensuales de ventas (unidades salientes)
            sales_by_month = sales.annotate(
                month=ExtractMonth('date')
            ).values('month').annotate(
                total_units=Sum('quantity')  # Suma de las cantidades vendidas
            ).order_by('month')
            
            # Datos mensuales de compras (unidades entrantes)
            purchases_by_month = purchases.annotate(
                month=ExtractMonth('date')
            ).values('month').annotate(
                total_units=Sum('quantity')  # Suma de las cantidades compradas
            ).order_by('month')
            
            # Convertir QuerySets en diccionarios para facilitar el acceso
            sales_dict = {item['month']: item['total_units'] or 0 for item in sales_by_month}
            purchases_dict = {item['month']: item['total_units'] or 0 for item in purchases_by_month}
            
            # Generar el resultado final con datos para todos los meses
            for month in range(1, 13):
                monthly_data.append({
                    "name": month_names[month],
                    "entradas": purchases_dict.get(month, 0),
                    "salidas": sales_dict.get(month, 0)
                })
            
            return Response(monthly_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
