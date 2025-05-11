from apps.company.repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self):
        self.repository = CompanyRepository()

    def get_all(self):
        return self.repository.get_all()

    def get_by_user(self, user):
        return self.repository.get_by_user(user)

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def create(self, company, user):
        company.user = user
        return self.repository.create(company)

    def update(self, company):
        return self.repository.update(company)

    def delete(self, id):
        return self.repository.delete(id)
