from apps.product.models import Product


class ProductRepository:

    @staticmethod
    def get_all():
        return Product.objects.all()

    @staticmethod
    def get_by_id(id):
        return Product.objects.get(id=id)

    @staticmethod
    def create(product):
        product.save()
        return product

    @staticmethod
    def update(product):
        product.save()
        return product

    @staticmethod
    def delete(id):
        return Product.objects.delete(id=id)

    @staticmethod
    def get_all_by_company(company):
        return Product.objects.filter(company=company)
