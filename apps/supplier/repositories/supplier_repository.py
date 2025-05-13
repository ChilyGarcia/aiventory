from apps.supplier.models import Supplier


class SupplierRepository:
    @staticmethod
    def get_all():
        return Supplier.objects.all()

    @staticmethod
    def get_by_id(id):
        return Supplier.objects.get(id=id)

    @staticmethod
    def create(supplier):
        supplier.save()
        return supplier

    @staticmethod
    def update(supplier):
        supplier.save()
        return supplier

    @staticmethod
    def delete(id):
        return Supplier.objects.delete(id=id)

    @staticmethod
    def get_all_by_company(company):
        return Supplier.objects.filter(company=company)
