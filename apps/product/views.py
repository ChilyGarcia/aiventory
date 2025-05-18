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
from itertools import chain


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
        self.company_service = CompanyService()
        
    @action(detail=False, methods=["get"], url_path="recent-movements")
    @custom_permission_required("view_products")
    def recent_movements(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Obtener límite (por defecto 5)
            limit = request.query_params.get("limit", 5)
            try:
                limit = int(limit)
                if limit <= 0:
                    limit = 5
            except ValueError:
                limit = 5
            
            # Consultar ventas recientes
            sales = Sale.objects.filter(company__in=companies).select_related('product').order_by('-date')[:limit]
            
            # Consultar compras recientes
            purchases = Purchase.objects.filter(company__in=companies).select_related('product').order_by('-date')[:limit]
            
            # Combinar y ordenar ambos conjuntos
            combined_movements = list(chain(sales, purchases))
            combined_movements.sort(key=lambda x: x.date, reverse=True)
            combined_movements = combined_movements[:limit]
            
            # Formatear los resultados
            result = []
            for item in combined_movements:
                movement_type = "Venta" if isinstance(item, Sale) else "Compra"
                if movement_type == "Venta":
                    result.append({
                        "id": item.id,
                        "type": movement_type,
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "date": item.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": float(item.total_price),
                        "unit_value": float(item.unit_price),
                        "person": item.customer if movement_type == "Venta" else item.supplier,
                        "stock_change": -item.quantity,
                        "sold_by": item.sold_by.get_full_name() if item.sold_by else "Usuario eliminado"
                    })
                else:  # Compra
                    result.append({
                        "id": item.id,
                        "type": movement_type,
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "date": item.date.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": float(item.total_cost),
                        "unit_value": float(item.unit_cost),
                        "person": item.supplier,
                        "stock_change": item.quantity
                    })
            
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                    {"error": "No tienes permiso para actualizar este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                updated_product = serializer.save(company=product.company)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=["get"],
        url_path="statistics",
        url_name="product-statistics",
    )
    @custom_permission_required("view_products")
    def statistics(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            stats = {
                "total_products": 0,
                "total_stock": 0,
                "inventory_value": 0,
                "low_stock": 0,
                "out_of_stock": 0,
            }

            LOW_STOCK_THRESHOLD = 5

            for company in companies:
                products = self.service.get_all_by_company(company)

                stats["total_products"] += len(products)

                total_stock = sum(p.stock for p in products)
                stats["total_stock"] += total_stock

                inventory_value = sum(p.price * p.stock for p in products)
                stats["inventory_value"] += inventory_value

                low_stock_units = sum(
                    p.stock for p in products if 0 < p.stock < LOW_STOCK_THRESHOLD
                )
                stats["low_stock"] += low_stock_units

                out_of_stock = sum(1 for p in products if p.stock == 0)
                stats["out_of_stock"] += out_of_stock

            return Response(stats)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=["get"], url_path="profitability")
    @custom_permission_required("view_products")
    def profitability(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            # Obtener límite de resultados (por defecto todos los productos)
            limit = request.query_params.get("limit", None)
            try:
                if limit:
                    limit = int(limit)
                    if limit <= 0:
                        limit = None
            except ValueError:
                limit = None
                
            # Obtener el tipo de ordenamiento
            sort_by = request.query_params.get("sort_by", "margin_percent")
            if sort_by not in ["margin_percent", "margin_value", "sales_volume"]:
                sort_by = "margin_percent"
                
            # Obtenemos todos los productos de las compañías del usuario
            all_products = []
            for company in companies:
                products = self.service.get_all_by_company(company)
                all_products.extend(products)
                
            # Calculamos métricas de rentabilidad para cada producto
            from django.db.models import Sum, Count
            from apps.sale.models import Sale
            from apps.purchase.models import Purchase
            
            product_metrics = []
            
            for product in all_products:
                # Obtenemos las ventas del producto
                sales = Sale.objects.filter(
                    product=product,
                    company__in=companies
                ).aggregate(
                    total_sales=Sum('total_price'),
                    total_quantity=Sum('quantity'),
                    transactions=Count('id')
                )
                
                # Obtenemos las compras del producto
                purchases = Purchase.objects.filter(
                    product=product,
                    company__in=companies
                ).aggregate(
                    total_cost=Sum('total_cost'),
                    total_quantity=Sum('quantity')
                )
                
                # Calculamos las métricas de rentabilidad
                total_sales = sales['total_sales'] or 0
                total_quantity_sold = sales['total_quantity'] or 0
                total_cost = purchases['total_cost'] or 0
                total_quantity_purchased = purchases['total_quantity'] or 0
                
                # Evitar división por cero
                avg_sale_price = total_sales / total_quantity_sold if total_quantity_sold > 0 else product.price
                avg_purchase_price = total_cost / total_quantity_purchased if total_quantity_purchased > 0 else 0
                
                # Cálculo de márgenes
                margin_value = avg_sale_price - avg_purchase_price
                margin_percent = (margin_value / avg_sale_price * 100) if avg_sale_price > 0 else 0
                
                product_metrics.append({
                    "id": product.id,
                    "name": product.name,
                    "current_price": float(product.price),
                    "current_stock": product.stock,
                    "avg_purchase_price": float(avg_purchase_price),
                    "avg_sale_price": float(avg_sale_price),
                    "margin_value": float(margin_value),
                    "margin_percent": float(margin_percent),
                    "sales_volume": total_quantity_sold,
                    "sales_value": float(total_sales),
                    "transactions": sales['transactions'] or 0
                })
            
            # Ordenamos por el campo seleccionado
            if sort_by == "margin_percent":
                product_metrics.sort(key=lambda x: x["margin_percent"], reverse=True)
            elif sort_by == "margin_value":
                product_metrics.sort(key=lambda x: x["margin_value"], reverse=True)
            elif sort_by == "sales_volume":
                product_metrics.sort(key=lambda x: x["sales_volume"], reverse=True)
                
            # Aplicamos el límite si se especificó
            if limit:
                product_metrics = product_metrics[:limit]
                
            return Response(product_metrics, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=["get"], url_path="inventory-rotation")
    @custom_permission_required("view_products")
    def inventory_rotation(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Obtener límite de resultados (por defecto todos los productos)
            limit = request.query_params.get("limit", None)
            try:
                if limit:
                    limit = int(limit)
                    if limit <= 0:
                        limit = None
            except ValueError:
                limit = None
            
            # Parámetro opcional para filtrar productos sin stock
            include_zero_stock = request.query_params.get("include_zero_stock", "false").lower() == "true"
            
            # Definimos criterios para considerar un producto de baja rotación (en días)
            ROTATION_THRESHOLDS = {
                "critical": 120,  # Más de 120 días sin vender = rotación crítica
                "low": 60,       # Entre 60 y 120 días = rotación baja
                "normal": 30     # Entre 30 y 60 días = rotación normal
                # Menos de 30 días = rotación alta
            }
            
            # Obtenemos todos los productos de las compañías del usuario
            all_products = []
            for company in companies:
                products = self.service.get_all_by_company(company)
                if not include_zero_stock:
                    products = [p for p in products if p.stock > 0]
                all_products.extend(products)
            
            from django.db.models import Max
            from apps.sale.models import Sale
            from datetime import datetime, timezone, timedelta
            from django.utils import timezone as django_timezone
            
            # Usamos timezone de Django para obtener la hora actual
            today = django_timezone.now()
            
            # Analizamos la rotación de cada producto
            rotation_data = []
            
            for product in all_products:
                # Buscamos la fecha de la última venta
                last_sale = Sale.objects.filter(
                    product=product,
                    company__in=companies
                ).aggregate(last_date=Max('date'))
                
                # Calculamos días desde la última venta
                last_sale_date = last_sale['last_date']
                
                if last_sale_date:
                    # Aseguramos que last_sale_date tenga timezone si no lo tiene
                    if last_sale_date.tzinfo is None:
                        last_sale_date = last_sale_date.replace(tzinfo=django_timezone.utc)
                    
                    # Calculamos la diferencia pero nos aseguramos que no sea negativa
                    days_diff = (today - last_sale_date).days
                    days_since_last_sale = max(0, days_diff)  # Nunca negativo
                else:
                    # Si nunca se ha vendido, usamos un valor alto
                    days_since_last_sale = 999  # Nunca vendido
                    last_sale_date = None
                
                # Determinamos la categoría de rotación
                if days_since_last_sale >= ROTATION_THRESHOLDS['critical']:
                    rotation_category = "Crítica"
                elif days_since_last_sale >= ROTATION_THRESHOLDS['low']:
                    rotation_category = "Baja"
                elif days_since_last_sale >= ROTATION_THRESHOLDS['normal']:
                    rotation_category = "Normal"
                else:
                    rotation_category = "Alta"
                
                # Calculamos el valor del inventario estancado
                inventory_value = float(product.price * product.stock)
                
                # Calculamos ventas del último año para el índice de rotación
                from django.db.models import Sum
                from datetime import timedelta
                
                one_year_ago = today - timedelta(days=365)
                
                yearly_sales = Sale.objects.filter(
                    product=product,
                    company__in=companies,
                    date__gte=one_year_ago
                ).aggregate(total_quantity=Sum('quantity'))
                
                total_sales_last_year = yearly_sales['total_quantity'] or 0
                
                # Índice de rotación = Ventas anuales / Stock promedio
                # Usamos el stock actual como aproximación al stock promedio
                rotation_index = total_sales_last_year / product.stock if product.stock > 0 else 0
                
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "current_stock": product.stock,
                    "days_since_last_sale": days_since_last_sale,
                    "last_sale_date": last_sale_date.strftime("%Y-%m-%d") if last_sale_date else "Nunca vendido",
                    "rotation_category": rotation_category,
                    "inventory_value": inventory_value,
                    "rotation_index": float(rotation_index),
                    "total_sales_last_year": total_sales_last_year
                }
                
                rotation_data.append(product_data)
            
            # Ordenamos por días desde la última venta (descendente)
            rotation_data.sort(key=lambda x: x["days_since_last_sale"], reverse=True)
            
            # Aplicamos el límite si se especificó
            if limit:
                rotation_data = rotation_data[:limit]
                
            # Calculamos estadísticas globales
            total_products = len(rotation_data)
            critical_rotation_products = sum(1 for p in rotation_data if p["rotation_category"] == "Crítica")
            critical_inventory_value = sum(p["inventory_value"] for p in rotation_data if p["rotation_category"] == "Crítica")
            
            response_data = {
                "summary": {
                    "total_products": total_products,
                    "critical_rotation_products": critical_rotation_products,
                    "critical_inventory_value": float(critical_inventory_value),
                    "rotation_thresholds": ROTATION_THRESHOLDS
                },
                "products": rotation_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="purchase-forecast")
    @custom_permission_required("view_products")
    def purchase_forecast(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            # Obtener límite de resultados (por defecto muestra todos los productos)
            limit = request.query_params.get("limit", None)
            try:
                if limit:
                    limit = int(limit)
                    if limit <= 0:
                        limit = None
            except ValueError:
                limit = None
                
            # Parámetro para filtrar productos con stock bajo un umbral
            min_stock_threshold = request.query_params.get("min_stock", 10) 
            try:
                min_stock_threshold = int(min_stock_threshold)
            except ValueError:
                min_stock_threshold = 10
                
            # Parámetro para mostrar todos los productos (sin filtrar)
            show_all = request.query_params.get("show_all", "false").lower() == "true"
                
            # Periodo de análisis en días (para calcular la velocidad de venta)
            analysis_period_days = request.query_params.get("period", 30)
            try:
                analysis_period_days = int(analysis_period_days)
                if analysis_period_days <= 0:
                    analysis_period_days = 30
            except ValueError:
                analysis_period_days = 30
                
            # Tiempo de entrega estimado en días (de pedido a recepción)
            lead_time_days = request.query_params.get("lead_time", 7)
            try:
                lead_time_days = int(lead_time_days)
                if lead_time_days < 0:
                    lead_time_days = 7
            except ValueError:
                lead_time_days = 7
            
            # Obtener todos los productos (con stock > 0 o todos)
            all_products = []
            for company in companies:
                products = self.service.get_all_by_company(company)
                all_products.extend(products)
                
            # Importar módulos necesarios
            from django.db.models import Sum
            from apps.sale.models import Sale
            from django.utils import timezone
            from datetime import timedelta
            import math
            
            # Fecha de inicio del período de análisis
            now = timezone.now()
            start_date = now - timedelta(days=analysis_period_days)
            
            # Lista para almacenar los resultados
            forecast_data = []
            
            for product in all_products:
                # Obtener ventas del periodo de análisis
                sales_in_period = Sale.objects.filter(
                    product=product,
                    company__in=companies,
                    date__gte=start_date
                ).aggregate(total_quantity=Sum('quantity'))
                
                total_sold = sales_in_period['total_quantity'] or 0
                
                # Calcular la tasa de venta diaria
                daily_sales_rate = total_sold / analysis_period_days if analysis_period_days > 0 else 0
                
                # Stock actual
                current_stock = product.stock
                
                # Días hasta agotamiento del stock (si la tasa de venta es > 0)
                # Limitamos a un máximo de 3650 días (10 años) para evitar errores de rango de fecha
                if daily_sales_rate > 0:
                    days_until_stockout = min(3650, math.ceil(current_stock / daily_sales_rate))
                else:
                    days_until_stockout = None
                
                # Fecha estimada de agotamiento
                stockout_date = now + timedelta(days=days_until_stockout) if days_until_stockout is not None else None
                
                # Determinar si es necesario hacer un pedido pronto
                # (si el stock se agotará en un tiempo menor o igual al tiempo de entrega + un margen de seguridad)
                reorder_needed = days_until_stockout is not None and days_until_stockout <= (lead_time_days + 5)  # 5 días de margen
                
                # Fecha sugerida para hacer el pedido
                # (fecha de agotamiento - tiempo de entrega - margen de seguridad)
                reorder_date = (stockout_date - timedelta(days=lead_time_days + 5)) if stockout_date else None
                
                # Cantidad sugerida para pedir
                # (tasa diaria * (tiempo de entrega + periodo de análisis como stock de seguridad))
                suggested_reorder_quantity = math.ceil(daily_sales_rate * (lead_time_days + analysis_period_days))
                
                # Prioridad de reabastecimiento (más bajo = más urgente)
                if days_until_stockout is None:
                    priority = "Baja"
                    days_to_reorder = None
                elif days_until_stockout <= lead_time_days:
                    priority = "Alta"
                    days_to_reorder = 0  # Pedir inmediatamente
                elif days_until_stockout <= lead_time_days * 2:
                    priority = "Media"
                    days_to_reorder = max(0, days_until_stockout - lead_time_days)
                else:
                    priority = "Baja"
                    days_to_reorder = max(0, days_until_stockout - lead_time_days - 5)
                
                forecast_item = {
                    "id": product.id,
                    "name": product.name,
                    "current_stock": current_stock,
                    "daily_sales_rate": round(daily_sales_rate, 2),
                    "total_sold_in_period": total_sold,
                    "days_until_stockout": days_until_stockout if days_until_stockout is not None else "N/A",
                    "stockout_date": stockout_date.strftime("%Y-%m-%d") if stockout_date else "N/A",
                    "reorder_needed": reorder_needed,
                    "days_to_reorder": days_to_reorder,
                    "suggested_quantity": suggested_reorder_quantity,
                    "priority": priority,
                    "unit_price": float(product.price),
                    "estimated_reorder_cost": float(product.price) * suggested_reorder_quantity,
                }
                
                forecast_data.append(forecast_item)
            
            # Filtrar los productos con stock por debajo del umbral o que necesiten reorden pronto
            # Solo si no se solicitó mostrar todos
            if not show_all:
                forecast_data = [p for p in forecast_data if p["current_stock"] <= min_stock_threshold or p["reorder_needed"]]
            
            # Ordenar por urgencia (días hasta el reorden)
            forecast_data.sort(key=lambda x: x["days_to_reorder"] if x["days_to_reorder"] is not None else 9999)
            
            # Aplicar límite si se especificó
            if limit:
                forecast_data = forecast_data[:limit]
                
            # Estadísticas generales
            products_to_reorder = sum(1 for p in forecast_data if p["reorder_needed"])
            total_reorder_cost = sum(p["estimated_reorder_cost"] for p in forecast_data if p["reorder_needed"])
            high_priority_count = sum(1 for p in forecast_data if p["priority"] == "Alta")
            
            response_data = {
                "summary": {
                    "analysis_period_days": analysis_period_days,
                    "lead_time_days": lead_time_days,
                    "total_products": len(forecast_data),
                    "products_to_reorder_soon": products_to_reorder,
                    "high_priority_count": high_priority_count,
                    "total_estimated_reorder_cost": float(total_reorder_cost)
                },
                "products": forecast_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

            year = request.query_params.get("year", datetime.now().year)
            try:
                year = int(year)
            except ValueError:
                year = datetime.now().year

            monthly_data = []

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

            sales = Sale.objects.filter(company__in=companies, date__year=year)

            purchases = Purchase.objects.filter(company__in=companies, date__year=year)

            sales_by_month = (
                sales.annotate(month=ExtractMonth("date"))
                .values("month")
                .annotate(total_units=Sum("quantity"))
                .order_by("month")
            )

            purchases_by_month = (
                purchases.annotate(month=ExtractMonth("date"))
                .values("month")
                .annotate(total_units=Sum("quantity"))
                .order_by("month")
            )
            sales_dict = {
                item["month"]: item["total_units"] or 0 for item in sales_by_month
            }
            purchases_dict = {
                item["month"]: item["total_units"] or 0 for item in purchases_by_month
            }
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
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
