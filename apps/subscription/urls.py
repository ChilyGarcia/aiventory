from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SubscriptionViewSet

router = DefaultRouter()
router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
]
