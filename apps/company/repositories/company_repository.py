from apps.company.models import Company


class CompanyRepository:
    @staticmethod
    def get_all():
        return Company.objects.all()

    @staticmethod
    def get_by_id(id):
        return Company.objects.get(id=id)

    @staticmethod
    def create(company):
        return Company.objects.create(**company)

    @staticmethod
    def update(company):
        return Company.objects.update(**company)

    @staticmethod
    def delete(id):
        return Company.objects.delete(id=id)
