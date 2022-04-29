import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[CeleryIntegration()]
    )

app = Celery(__name__)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

try:
    import ujson
except ImportError:
    pass
else:
    import kombu.serialization

    kombu.serialization.register(
        'ujson', ujson.dumps, ujson.loads,
        content_type='application/json'
    )


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
