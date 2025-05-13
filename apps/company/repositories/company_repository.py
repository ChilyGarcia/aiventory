from django.db import models
from apps.company.models import Company


class CompanyRepository:
    @staticmethod
    def get_all():
        return Company.objects.all()

    @staticmethod
    def get_by_user(user):
        # Obtener compañías donde el usuario es dueño o empleado
        if user.company:
            return Company.objects.filter(
                models.Q(user=user) | models.Q(id=user.company.id)
            ).distinct()
        return Company.objects.filter(user=user)

    @staticmethod
    def get_by_id(id):
        return Company.objects.get(id=id)

    @staticmethod
    def create(company):
        company.save()
        return company

    @staticmethod
    def update(company):
        company.save()
        return company

    @staticmethod
    def delete(id):
        company = Company.objects.get(id=id)
        company.delete()
        return True
