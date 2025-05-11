from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.company.services.company_service import CompanyService
from apps.company.serializers import CompanySerializer


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompanyService()

    def list(self, request):
        try:
            companies = self.service.get_all()
            serializer = CompanySerializer(companies, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            serializer = CompanySerializer(data=request.data)
            if serializer.is_valid():
                company = self.service.create(serializer.validated_data)
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
            serializer = CompanySerializer(company, data=request.data)
            if serializer.is_valid():
                updated_company = self.service.update(serializer.validated_data)
                response_serializer = CompanySerializer(updated_company)
                return Response(response_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
