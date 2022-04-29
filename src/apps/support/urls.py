from django.conf import settings
from django.urls import path
from django.views.decorators import csrf

from apps.support import views

urlpatterns = [
    path(f'{settings.ADMIN_PATH}monitor/', csrf.csrf_exempt(views.MonitorView.as_view()), name='monitor'),

    path('v1/blinger/webhook/', csrf.csrf_exempt(views.BlingerWebhookView.as_view()), name='blinger_webhook'),

]
