from apps.supplier.repositories.supplier_repository import SupplierRepository


class SupplierService:

    def __init__(self):
        self.repository = SupplierRepository()

    def create_supplier(self, supplier):
        return self.repository.create(supplier)

    def update_supplier(self, supplier):
        return self.repository.update(supplier)

    def delete_supplier(self, supplier):
        return self.repository.delete(supplier)

    def get_all_suppliers(self):
        return self.repository.get_all()

    def get_supplier_by_id(self, id):
        return self.repository.get_by_id(id)

    def get_all_suppliers_by_company(self, company):
        return self.repository.get_all_by_company(company)
