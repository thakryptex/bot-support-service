__all__ = ('CLIENT_KWARGS',)

from envparse import env
from django.conf import settings

CLIENT_KWARGS = {
    'base_url': settings.AUTH_API_ENDPOINT,
    'timeout': (env.float('AUTH_CONNECT_TIMEOUT_SEC', default=5.0),
                env.float('AUTH_TIMEOUT_SEC', default=5.0)),
}
