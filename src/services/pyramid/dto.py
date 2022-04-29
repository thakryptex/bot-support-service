from dataclasses import dataclass
from typing import List

from atlas_utils.common.base_dto import Dto


@dataclass
class HerbUserDto(Dto):
    id: int
    phone: str
    blocked: bool
    nickname: str = None


@dataclass
class HerbOrderFromListDto(Dto):
    id: int
    client_number: str
    order_created_at: str
    user_name: str
    user_phone: str
    status_code: str
    status_text: str
    total: float
    promocode: str
    redemption_amount: float
    redemption_date: str
    client_earning_sum: float = None
    promocode_earning_sum: float = None


@dataclass
class HerbOrdersListDto(Dto):
    pages: int
    items: List[HerbOrderFromListDto]


@dataclass
class HerbPositionDto(Dto):
    position_id: int
    product_name: str
    status: str
    position_sale: float
    cashback_percent: float
    cashback_amount: float
    cashback_subtype: str
    cashback_subtype_desc: str
    brand_name: str


@dataclass
class HerbOrderDto(Dto):
    id: int
    client_number: str
    order_created_at: str
    user_name: str
    status_code: str
    status_text: str
    promocode: str
    redemption_amount: float
    redemption_date: str
    total: float
    positions: List[HerbPositionDto]
