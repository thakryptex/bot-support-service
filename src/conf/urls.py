from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('healthcheck/', include('health_check.urls')),
    path('metrics', include('django_metrics.urls')),
    path(settings.ADMIN_PATH, admin.site.urls),
    path('', include('apps.support.urls')),
]
