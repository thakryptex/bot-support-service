from dataclasses import dataclass
from typing import List

from atlas_utils.common.base_dto import Dto


@dataclass
class OrderDto(Dto):
    guid: str
    client_number: str
    state: str
    status_code: str
    status_text: str
    total: str
    payed: str
    payment_type: str = 'cash_delivery'


@dataclass
class OrdersListDto(Dto):
    pages: int
    items: List[OrderDto]
