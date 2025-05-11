from apps.product.repositories.product_repository import ProductRepository


class ProductService:

    def __init__(self):
        self.repository = ProductRepository()

    def get_all_by_company(self, company):
        return self.repository.get_all_by_company(company)

    def get_all(self):
        return self.repository.get_all()

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def create(self, product):
        return self.repository.create(product)

    def update(self, product):
        return self.repository.update(product)

    def delete(self, id):
        return self.repository.delete(id)
