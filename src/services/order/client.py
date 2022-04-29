import logging

import requests
from atlas_utils.common.exceptions import ServiceUnavailable
from django.conf import settings

from services.order.factory import OrderListDtoFactory, OrderDtoFactory

logger = logging.getLogger(__name__)


class OrderAdapter:
    def __init__(self, order_domain):
        self.order_domain = order_domain

    def get_orders_list(self, token, page=1):
        url = self.order_domain + '/v2/order/list/'
        params = {'page': page, 'amount': 10}
        response = requests.get(url, params=params, headers={'token': token}, timeout=40)
        if response.ok:
            result = response.json()
            dto = OrderListDtoFactory.dto_from_dict(result)
            return dto
        else:
            raise ServiceUnavailable(f'Order get_orders_list error: {response.status_code}')

    def get_order_info(self, order_guid):
        url = self.order_domain + f'/v2/order/{order_guid}/'
        response = requests.get(url, timeout=40)
        if response.ok:
            result = response.json()
            dto = OrderDtoFactory.dto_from_dict(result)
            return dto
        else:
            raise ServiceUnavailable(f'Order get_order_info error: {response.status_code}')


order_adapter = OrderAdapter(settings.OMNIORDER_DOMAIN)
