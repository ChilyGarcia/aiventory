from apps.company.models import Company


class CompanyRepository:
    @staticmethod
    def get_all():
        return Company.objects.all()

    @staticmethod
    def get_by_user(user):
        # Obtener compañías donde el usuario es dueño
        owned_companies = Company.objects.filter(user=user).all()

        # Obtener la compañía donde el usuario es empleado
        if user.company:
            employee_company = [user.company]
        else:
            employee_company = []

        # Combinar ambas listas y eliminar duplicados
        return list(set(list(owned_companies) + employee_company))

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
