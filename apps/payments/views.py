from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WompiTransaction
from .serializers import WompiTransactionSerializer


class WompiTransactionViewSet(viewsets.ModelViewSet):
    queryset = WompiTransaction.objects.all()
    serializer_class = WompiTransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        return Response(
            {
                "message": "Pago simulado exitosamente",
                "transaction": WompiTransactionSerializer(transaction).data,
            },
            status=status.HTTP_201_CREATED,
        )
