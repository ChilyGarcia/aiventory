from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchasesViewSet

router = DefaultRouter()
router.register(r"", PurchasesViewSet, basename="purchases")

urlpatterns = [
    path("", include(router.urls)),
]
