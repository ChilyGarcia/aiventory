from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.company.services.company_service import CompanyService
from apps.users.decorators import custom_permission_required
from rest_framework.response import Response
from rest_framework import status
from apps.supplier.services.supplier_service import SupplierService
from apps.supplier.serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SupplierService()
        self.company_service = CompanyService()

    @custom_permission_required('view_supplier')
    def list(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            all_suppliers = []
            for company in companies:
                suppliers = self.service.get_all_suppliers_by_company(company)
                all_suppliers.extend(suppliers)

            serializer = SupplierSerializer(all_suppliers, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @custom_permission_required('view_supplier')
    def retrieve(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            supplier = self.service.get_by_id(pk)
            if not supplier:
                return Response({"error": "Proveedor no encontrado"},
                                status=status.HTTP_404_NOT_FOUND)

            if supplier.company not in companies:
                return Response(
                    {"error": "No tienes permiso para ver este producto"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = SupplierSerializer(supplier)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required('change_supplier')
    def update(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            supplier = self.service.get_by_id(pk)
            if not supplier:
                return Response({"error": "Proveedor no encontrado"},
                                status=status.HTTP_404_NOT_FOUND)

            if supplier.company not in companies:
                return Response(
                    {
                        "error":
                        "No tienes permiso para actualizar este proveedor"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = SupplierSerializer(supplier, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    @custom_permission_required('add_supplier')
    def create(self, request):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @custom_permission_required('delete_supplier')
    def destroy(self, request, pk=None):
        try:
            companies = self.company_service.get_all_by_user(request.user)
            if not companies:
                return Response(
                    {"error": "El usuario no tiene compañías asignadas"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            supplier = self.service.get_by_id(pk)
            if not supplier:
                return Response({"error": "Proveedor no encontrado"},
                                status=status.HTTP_404_NOT_FOUND)

            if supplier.company not in companies:
                return Response(
                    {
                        "error":
                        "No tienes permiso para eliminar este proveedor"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)
