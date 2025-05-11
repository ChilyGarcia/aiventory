from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth endpoints
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    # API endpoints
    path("api/", include("apps.company.urls")),
    path("api/", include("apps.product.urls")),
]
