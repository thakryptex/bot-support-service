from django.conf import settings

from services.pyramid.dto import HerbUserDto, HerbOrderFromListDto, HerbOrderDto, HerbPositionDto, HerbOrdersListDto


class HerbUserDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        item = item_dict['data']
        return HerbUserDto(
            id=item['id'],
            phone=item['phone'],
            blocked=item['blocked'],
            nickname=item['nick_name'],
        )


class HerbOrdersListDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        items = [HerbOrderFromListDto(
            id=item['id'],
            client_number=item['number'],
            order_created_at=item['order_created_at'],
            user_name=item['user_name'],
            user_phone=item['user_phone'],
            status_code=item['status'],
            status_text=item['status_description'],
            total=item['amount'],
            promocode=item['promocode'],
            redemption_amount=item['redemption_amount'],
            redemption_date=item['redemption_date'],
            client_earning_sum=item.get('client_earning_sum'),
            promocode_earning_sum=item.get('promocode_earning_sum'),
        ) for item in item_dict['data']['items']]
        total = item_dict['data']['totalItems']
        per_page = settings.PYRAMID_PAGE_LIMIT
        return HerbOrdersListDto(
            pages=total // per_page + (total % per_page > 0),
            items=items
        )


class HerbOrderDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        data = item_dict['data']
        return HerbOrderDto(
            id=data['id'],
            client_number=data['number'],
            order_created_at=data['createdAt'],
            user_name=data['userName'],
            status_code=data['status'],
            status_text=data['statusDescription'],
            promocode=data['promocode'],
            redemption_amount=data['redemptionAmount'],
            redemption_date=data['redemptionDate'],
            total=data['amount'],
            positions=[
                HerbPositionDto(
                    position_id=position['positionId'],
                    product_name=position['productName'],
                    status=position['status'],
                    position_sale=position['positionSale'],
                    cashback_percent=position['cashbackPercent'],
                    cashback_amount=position['cashbackAmount'],
                    cashback_subtype=position['cashbackSubtype'],
                    cashback_subtype_desc=position['cashbackSubtypeDescription'],
                    brand_name=position['brandName'],
                ) for position in data['positions']]
        )
