from rest_framework import viewsets, mixins
from .models import Plan
from .serializers import PlanSerializer
from rest_framework.permissions import AllowAny


class PlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
