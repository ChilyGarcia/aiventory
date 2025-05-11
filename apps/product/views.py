from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.product.services.product_service import ProductService
from apps.product.serializers import ProductSerializer
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ProductService()
        self.company_service = CompanyService()

    @custom_permission_required('view_products')
    def list(self, request):
        try:
            company = self.company_service.get_by_user(request.user)
            if not company:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products = self.service.get_all_by_company(company)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @custom_permission_required('view_products')
    def retrieve(self, request, pk=None):
        try:
            company = self.company_service.get_by_user(request.user)
            if not company:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = self.service.get_by_id(pk)
            if product.company != company:
                return Response(
                    {"error": "No tienes permiso para ver este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required('create_product')
    def create(self, request):
        try:
            company = self.company_service.get_by_user(request.user)
            if not company:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                product = serializer.save(company=company)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @custom_permission_required('edit_product')
    def update(self, request, pk=None):
        try:
            company = self.company_service.get_by_user(request.user)
            if not company:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = self.service.get_by_id(pk)
            if product.company != company:
                return Response(
                    {"error": "No tienes permiso para actualizar este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                updated_product = serializer.save(company=company)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required('delete_product')
    def destroy(self, request, pk=None):
        try:
            company = self.company_service.get_by_user(request.user)
            if not company:
                return Response(
                    {"error": "El usuario no tiene una compañía asignada"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = self.service.get_by_id(pk)
            if product.company != company:
                return Response(
                    {"error": "No tienes permiso para eliminar este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
