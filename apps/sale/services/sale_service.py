from apps.sale.repositories.sale_repository import SaleRepository


class SaleService:
    def __init__(self):
        self.repository = SaleRepository()

    def get_all_by_company(self, companies):
        return self.repository.get_all_by_company(companies)

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def create(self, sale):
        return self.repository.create(sale)

    def update(self, sale):
        return self.repository.update(sale)

    def delete(self, id):
        return self.repository.delete(id)
