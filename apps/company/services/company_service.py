from django.contrib.auth.models import Permission
from apps.company.repositories.company_repository import CompanyRepository
from apps.users.models import CustomUser


class CompanyService:
    def __init__(self):
        self.repository = CompanyRepository()

    def get_all(self):
        return self.repository.get_all()

    def get_all_by_user(self, user):
        return self.repository.get_by_user(user)

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def create(self, company):
        return self.repository.create(company)

    def update(self, company):
        return self.repository.update(company)

    def delete(self, id):
        return self.repository.delete(id)

    def assign_owner(self, user, company):
        company.user = user
        company.save()
        return company

    def is_user_owner(self, user, company):
        return company.user == user

    def update_employee_permissions(self, email, company, permissions):
        try:
            employee = CustomUser.objects.get(email=email)

            # Verificar que el empleado pertenece a la compañía
            if employee.company != company:
                return "El usuario no pertenece a esta compañía"

            # Limpiar permisos anteriores
            employee.custom_permissions.clear()

            # Asignar nuevos permisos
            for perm_name in permissions:
                try:
                    perm = Permission.objects.get(codename=perm_name)
                    employee.custom_permissions.add(perm)
                except Permission.DoesNotExist:
                    continue

            return True
        except CustomUser.DoesNotExist:
            return "Usuario no encontrado"
