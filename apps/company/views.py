from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.company.services.company_service import CompanyService
from apps.company.serializers import CompanySerializer
from apps.company.models import Company


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompanyService()

    def list(self, request):
        try:
            companies = self.service.get_by_user(request.user)
            serializer = CompanySerializer(companies, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if company.user != request.user:
                return Response(
                    {"error": "No tienes permiso para ver esta compañía"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            serializer = CompanySerializer(data=request.data)
            if serializer.is_valid():
                # Crear una instancia de Company pero no guardarla en la base de datos aún
                company = Company(**serializer.validated_data)
                # Asignar el usuario y guardar
                company = self.service.create(company, request.user)
                response_serializer = CompanySerializer(company)
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if company.user != request.user:
                return Response(
                    {"error": "No tienes permiso para actualizar esta compañía"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = CompanySerializer(company, data=request.data)
            if serializer.is_valid():
                updated_company = serializer.save()
                updated_company = self.service.update(updated_company)
                response_serializer = CompanySerializer(updated_company)
                return Response(response_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if company.user != request.user:
                return Response(
                    {"error": "No tienes permiso para eliminar esta compañía"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
