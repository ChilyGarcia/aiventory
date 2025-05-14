from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.sale.services.sale_service import SaleService
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status
from apps.sale.serializers import SaleSerializer
from apps.product.models import Product


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
            sales = self.service.get_all()
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
