from apps.sale.models import Sale


class SaleRepository:
    @staticmethod
    def create(sale_data):
        return Sale.objects.create(**sale_data)

    @staticmethod
    def get_all():
        return Sale.objects.all()

    @staticmethod
    def get_by_id(id):
        return Sale.objects.get(id=id)

    @staticmethod
    def update(sale):
        sale.save()
        return sale

    @staticmethod
    def delete(id):
        sale = Sale.objects.get(id=id)
        sale.delete()
        return True
