import logging

import requests
from atlas_utils.common.exceptions import ServiceUnavailable
from django.conf import settings

from services.pyramid.factory import HerbUserDtoFactory, HerbOrderDtoFactory, HerbOrdersListDtoFactory

logger = logging.getLogger(__name__)


class PyramidAdapter:
    def __init__(self, pyramid_domain):
        self.pyramid_domain = pyramid_domain

    def is_herb_user(self, token):
        url = self.pyramid_domain + '/api/v1/herbamans/is-exist'
        response = requests.get(url, headers={'token': token}, timeout=15)
        if response.ok:
            result = response.json()
            dto = HerbUserDtoFactory.dto_from_dict(result)
            return dto
        elif response.status_code == 404 and response.headers.get('Content-Type') == 'application/json':
            return False
        else:
            raise ServiceUnavailable(f'Pyramid is_herb_user error: {response.status_code}')

    def get_orders_list(self, token, herb_id, page=1):
        url = self.pyramid_domain + f'/api/v1/herbamans/{herb_id}/orders/'
        params = {'offset': (page - 1) * 10, 'limit': settings.PYRAMID_PAGE_LIMIT,
                  'order_by': 'order_created_at', 'order_direction': 'desc'}
        response = requests.get(url, params=params, headers={'token': token}, timeout=15)
        if response.ok:
            result = response.json()
            dto = HerbOrdersListDtoFactory.dto_from_dict(result)
            return dto
        else:
            raise ServiceUnavailable(f'Pyramid get_orders_list error: {response.status_code}')

    def get_order_info(self, token, herb_id, client_number):
        url = self.pyramid_domain + f'/api/v1/herbamans/{herb_id}/orders/{client_number}'
        response = requests.get(url, headers={'token': token}, timeout=15)
        if response.ok:
            result = response.json()
            dto = HerbOrderDtoFactory.dto_from_dict(result)
            return dto
        else:
            raise ServiceUnavailable(f'Pyramid get_order_info error: {response.status_code}')


pyramid_client = PyramidAdapter(settings.PYRAMID_DOMAIN)
