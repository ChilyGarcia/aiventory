from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from apps.company.services.company_service import CompanyService
from apps.company.serializers import CompanySerializer
from apps.users.decorators import custom_permission_required
from apps.users.models import CustomUser, Role
from apps.subscription.models import Subscription
from django.contrib.auth.models import Permission


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CompanyService()

    def list(self, request):
        try:
            companies = self.service.get_all_by_user(request.user)
            serializer = CompanySerializer(
                companies,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if not company:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if company.user != request.user:
                msg = "No tienes permiso para ver esta compañía"
                return Response({"error": msg},
                                status=status.HTTP_403_FORBIDDEN)
            serializer = CompanySerializer(company, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            active_subscription = Subscription.objects.filter(
                user=request.user, is_active=True,
                end_date__gt=timezone.now()).first()

            if not active_subscription:
                return Response(
                    {
                        "error":
                        "Necesitas una suscripción activa para crear una compañía. "
                        "Por favor, adquiere un plan."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            entrepreneur_role, _ = Role.objects.get_or_create(
                name=Role.ENTREPRENEUR)

            request.user.role = entrepreneur_role

            permissions = [
                "create_company",
                "manage_company_users",
                "view_companies",
                "manage_employees",
                "view_products",
                "create_product",
                "edit_product",
                "delete_product",
            ]

            for perm_name in permissions:
                try:
                    perm = Permission.objects.get(codename=perm_name)
                    request.user.custom_permissions.add(perm)
                except Permission.DoesNotExist:
                    continue

            request.user.save()

            existing_company = self.service.get_all_by_user(
                request.user).first()
            if existing_company:
                return Response(
                    {
                        "error":
                        "Ya tienes una compañía registrada. "
                        "Tu plan actual no permite crear más compañías."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = CompanySerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                company = serializer.save()
                self.service.assign_owner(request.user, company)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @custom_permission_required("manage_company_users")
    @action(detail=True, methods=["post"])
    def add_employee(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)

            if company.user != request.user:
                msg = "Solo el dueño puede agregar empleados"
                return Response({"error": msg},
                                status=status.HTTP_403_FORBIDDEN)

            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return Response(
                    {"error": "Email y password son requeridos"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            employee_role = Role.objects.get(name=Role.EMPLOYEE)

            new_employee = CustomUser.objects.create_user(email=email,
                                                          password=password,
                                                          role=employee_role,
                                                          company=company)

            perm = Permission.objects.get(codename="view_products")
            new_employee.custom_permissions.add(perm)

            return Response({"message": "Empleado creado exitosamente"})
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @custom_permission_required("manage_company_users")
    @action(detail=True, methods=["post"])
    def update_employee_permissions(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if not company:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not self.service.is_user_owner(request.user, company):
                msg = "No tienes permiso para actualizar permisos"
                return Response({"error": msg},
                                status=status.HTTP_403_FORBIDDEN)

            email = request.data.get("email")
            permissions = request.data.get("permissions", [])
            if not email:
                return Response(
                    {"error": "El email es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = self.service.update_employee_permissions(
                email, company, permissions)
            if isinstance(result, str):
                return Response({"error": result},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Permisos actualizados exitosamente"})
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if not company:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not self.service.is_user_owner(request.user, company):
                msg = "No tienes permiso para actualizar"
                return Response({"error": msg},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = CompanySerializer(
                company,
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            company = self.service.get_by_id(pk)
            if not company:
                return Response(
                    {"error": "Compañía no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not self.service.is_user_owner(request.user, company):
                msg = "No tienes permiso para eliminar esta compañía"
                return Response(
                    {"error": msg},
                    status=status.HTTP_403_FORBIDDEN,
                )

            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_404_NOT_FOUND)
