from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.purchase.services.purchase_service import PurchaseService
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Sum, Avg
from apps.purchase.serializers import PurchaseSerializer
from apps.product.models import Product
from apps.purchase.models import Purchase


class PurchasesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PurchaseService()
        self.company_service = CompanyService()

    @custom_permission_required("view_purchases")
    def list(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            purchases = self.service.get_all_by_company(companies)
            return Response(
                PurchaseSerializer(purchases, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("view_purchases")
    def retrieve(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            purchase = self.service.get_by_id(pk)
            if not purchase:
                return Response(
                    {"error": "Compra no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if purchase.company not in companies:
                return Response(
                    {"error": "No tienes permiso para ver esta compra"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = PurchaseSerializer(purchase)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("create_purchase")
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

            serializer = PurchaseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(company=company)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("edit_purchase")
    def update(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            purchase = self.service.get_by_id(pk)
            if not purchase:
                return Response(
                    {"error": "Compra no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if purchase.company not in companies:
                return Response(
                    {"error": "No tienes permiso para actualizar esta compra"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = PurchaseSerializer(purchase, data=request.data)
            if serializer.is_valid():
                serializer.save(company=purchase.company)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @custom_permission_required("delete_purchase")
    def destroy(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            purchase = self.service.get_by_id(pk)
            if not purchase:
                return Response(
                    {"error": "Compra no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if purchase.company not in companies:
                return Response(
                    {"error": "No tienes permiso para eliminar esta compra"},
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
    @custom_permission_required("view_purchases")
    def statistics(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Filtramos las compras por la(s) compañía(s) del usuario
            purchases = Purchase.objects.filter(company__in=companies)

            # Calculamos el total de compras en dinero
            total_purchases = purchases.aggregate(total=Sum("total_cost"))

            # Calculamos el promedio de dinero por compra
            average_purchase = purchases.aggregate(average=Avg("total_cost"))

            return Response(
                {
                    "total_purchases": total_purchases["total"] or 0,
                    "average_purchase": average_purchase["average"] or 0,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
