from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.sale.services.sale_service import SaleService
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Sum, Avg
from django.db.models.functions import ExtractMonth
from apps.sale.serializers import SaleSerializer
from apps.product.models import Product
from apps.sale.models import Sale
from apps.purchase.models import Purchase
from datetime import datetime


class SalesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SaleService()
        self.company_service = CompanyService()

    @custom_permission_required("view_sales")
    def list(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            sales = self.service.get_all_by_company(companies)
            return Response(
                SaleSerializer(sales, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("view_sales")
    def retrieve(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            sale = self.service.get_by_id(pk)
            if not sale:
                return Response(
                    {"error": "Venta no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if sale.company not in companies:
                return Response(
                    {"error": "No tienes permiso para ver esta venta"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = SaleSerializer(sale)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("create_sale")
    def create(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            company = companies[0]

            product_id = request.data.get("product")
            product = Product.objects.filter(id=product_id, company=company).first()
            if not product:
                return Response(
                    {"error": "El producto no existe o no pertenece a tu compañía"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = SaleSerializer(data=request.data)
            if serializer.is_valid():
                sale = serializer.save(company=company, sold_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("edit_sale")
    def update(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            sale = self.service.get_by_id(pk)
            if not sale:
                return Response(
                    {"error": "Venta no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if sale.company not in companies:
                return Response(
                    {"error": "No tienes permiso para actualizar esta venta"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = SaleSerializer(sale, data=request.data)
            if serializer.is_valid():
                updated_sale = serializer.save(company=sale.company)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("delete_sale")
    def destroy(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            sale = self.service.get_by_id(pk)
            if not sale:
                return Response(
                    {"error": "Venta no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if sale.company not in companies:
                return Response(
                    {"error": "No tienes permiso para eliminar esta venta"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    @custom_permission_required("view_sales")
    def statistics(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Filtramos las ventas por la(s) compañía(s) del usuario
            sales = Sale.objects.filter(company__in=companies)

            # Calculamos el total de ventas en dinero
            total_sales = sales.aggregate(total=Sum("total_price"))

            # Calculamos el promedio de dinero por venta
            average_sale = sales.aggregate(average=Avg("total_price"))

            return Response(
                {
                    "total_sales": total_sales["total"] or 0,
                    "average_sale": average_sale["average"] or 0,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="top-products")
    @custom_permission_required("view_sales")
    def top_products(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Obtener límite de resultados (por defecto 10)
            limit = request.query_params.get("limit", 10)
            try:
                limit = int(limit)
                if limit <= 0:
                    limit = 10
            except ValueError:
                limit = 10

            # Filtrar por periodo (opcional)
            period = request.query_params.get("period", None)
            sales_query = Sale.objects.filter(company__in=companies)

            if period == "month":
                # Último mes
                from datetime import datetime, timedelta

                last_month = datetime.now() - timedelta(days=30)
                sales_query = sales_query.filter(date__gte=last_month)
            elif period == "year":
                # Último año
                from datetime import datetime, timedelta

                last_year = datetime.now() - timedelta(days=365)
                sales_query = sales_query.filter(date__gte=last_year)

            # Agrupar ventas por producto y sumar cantidades
            # Utilizamos annotate y Sum para agrupar por producto y calcular totales
            from django.db.models import Count, F

            top_products = (
                sales_query.values("product", "product__name", "product__price")
                .annotate(
                    total_quantity=Sum("quantity"),
                    total_sales=Sum("total_price"),
                    count=Count("id"),
                )
                .order_by("-total_quantity")[:limit]
            )

            # Preparamos los datos para la visualización
            result = []
            for item in top_products:
                result.append(
                    {
                        "id": item["product"],
                        "name": item["product__name"],
                        "quantity_sold": item["total_quantity"],
                        "total_sales": float(item["total_sales"]),
                        "unit_price": float(item["product__price"]),
                        "transactions": item["count"],
                    }
                )

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="monthly-chart")
    @custom_permission_required("view_sales")
    def monthly_chart(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Año para el que queremos obtener los datos (por defecto el año actual)
            year = request.query_params.get("year", datetime.now().year)
            try:
                year = int(year)
            except ValueError:
                year = datetime.now().year

            # Diccionario para almacenar los datos de cada mes
            monthly_data = []

            # Nombres abreviados de los meses en español
            month_names = {
                1: "Ene",
                2: "Feb",
                3: "Mar",
                4: "Abr",
                5: "May",
                6: "Jun",
                7: "Jul",
                8: "Ago",
                9: "Sep",
                10: "Oct",
                11: "Nov",
                12: "Dic",
            }

            # Obtener las ventas y compras del año especificado
            sales = Sale.objects.filter(company__in=companies, date__year=year)

            purchases = Purchase.objects.filter(company__in=companies, date__year=year)

            # Datos mensuales de ventas
            sales_by_month = (
                sales.annotate(month=ExtractMonth("date"))
                .values("month")
                .annotate(total=Sum("total_price"))
                .order_by("month")
            )

            # Datos mensuales de compras
            purchases_by_month = (
                purchases.annotate(month=ExtractMonth("date"))
                .values("month")
                .annotate(total=Sum("total_cost"))
                .order_by("month")
            )

            # Convertir QuerySets en diccionarios para facilitar el acceso
            sales_dict = {
                item["month"]: float(item["total"]) for item in sales_by_month
            }
            purchases_dict = {
                item["month"]: float(item["total"]) for item in purchases_by_month
            }

            # Generar el resultado final con datos para todos los meses
            for month in range(1, 13):
                monthly_data.append(
                    {
                        "name": month_names[month],
                        "entradas": purchases_dict.get(month, 0),
                        "salidas": sales_dict.get(month, 0),
                    }
                )

            return Response(monthly_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
