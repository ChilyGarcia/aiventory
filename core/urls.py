from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth endpoints
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    # API endpoints
    path("api/", include("apps.company.urls")),
    path("api/", include("apps.product.urls")),
    path("api/", include("apps.supplier.urls")),
    path("api/", include("apps.plan.urls")),
    path("api/", include("apps.subscription.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/sales/", include("apps.sale.urls")),
    path("api/purchases/", include("apps.purchase.urls")),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
