from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        active_subscription = Subscription.objects.filter(
            user=request.user, is_active=True, end_date__gt=timezone.now()
        ).first()

        if active_subscription:
            return Response(
                {
                    "error": "Ya tienes una suscripción activa que vence el "
                    f"{active_subscription.end_date.strftime('%Y-%m-%d')}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["user"] = request.user.id
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
