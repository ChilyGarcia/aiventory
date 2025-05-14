from apps.purchase.models import Purchase


class PurchaseService:
    def get_all(self):
        return Purchase.objects.all()

    def get_by_id(self, purchase_id):
        try:
            return Purchase.objects.get(id=purchase_id)
        except Purchase.DoesNotExist:
            return None

    def create(self, purchase_data):
        return Purchase.objects.create(**purchase_data)

    def update(self, purchase_id, purchase_data):
        purchase = self.get_by_id(purchase_id)
        if not purchase:
            return None

        for key, value in purchase_data.items():
            setattr(purchase, key, value)
        purchase.save()
        return purchase

    def delete(self, purchase_id):
        purchase = self.get_by_id(purchase_id)
        if not purchase:
            return False
        purchase.delete()
        return True
