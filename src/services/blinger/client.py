import logging

import requests
from atlas_utils.common.exceptions import ServiceUnavailable
from django.conf import settings

logger = logging.getLogger(__name__)


class BlingerAdapter:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def send_message(self, user_id, name, phone, text, photo=None):
        url = self.url + '/custom_channel_webhook'
        params = {
            "user_id": settings.BLINGER_USER_ID,
            "custom_channel_id": settings.BLINGER_CHANNEL_ID,
            "client_id": user_id,
            "client_name": name,
            "client_phone": phone,
            "type": 'text' if text else 'image',
            "data": text if text else photo,
        }
        response = requests.post(url, params=params, headers={'Authorization': f'Bearer {self.token}'}, timeout=30)
        if response.ok:
            return True
        else:
            raise ServiceUnavailable(f'BlingerAdapter send_message error: {response.status_code}')


blinger_adapter = BlingerAdapter(settings.BLINGER_WEBHOOK_URL, settings.BLINGER_TOKEN)
