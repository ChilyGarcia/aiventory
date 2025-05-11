from apps.company.models import Company


class CompanyRepository:
    @staticmethod
    def get_all():
        return Company.objects.all()

    @staticmethod
    def get_by_user(user):
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
        return Company.objects.delete(id=id)
