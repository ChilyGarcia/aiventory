from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import WompiTransactionViewSet

router = DefaultRouter()
router.register(r"transactions", WompiTransactionViewSet, basename="wompi-transaction")

urlpatterns = [
    path("", include(router.urls)),
]
