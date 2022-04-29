from django.conf import settings

from services.client import BaseClient
from services.lobster.settings import CLIENT_KWARGS

__all__ = ('LobsterClient',)


class LobsterClient(BaseClient):
    headers = {"Content-Type": "application/json", "referrer": settings.AUTH_API_REFERRER, "x-language": "ru",
               "service-slug": "bot-support-service"}

    def check_auth_and_get_token(self, phone):
        response = self._post('/lor', json={'also_login': True, 'phone': phone}, headers=self.headers)
        return response['meta']['token']


lobster_client = LobsterClient(**CLIENT_KWARGS)
