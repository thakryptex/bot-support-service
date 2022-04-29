from services.order.dto import OrdersListDto, OrderDto


class OrderDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        item = item_dict['data']
        return OrderDto(
            guid=item['guid'],
            client_number=item['clientNumber'],
            state=item['state'],
            status_code=item['status']['code'],
            status_text=item['status']['text'],
            total=item['prices']['total'],
            payed=item['paymentSum'],
            payment_type=item['paymentType'],
        )


class OrderListDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        items = [OrderDto(
            guid=item['guid'],
            client_number=item['clientNumber'],
            state=item['state'],
            status_code=item['status']['code'],
            status_text=item['status']['text'],
            total=item['price']['total'],
            payed=item['paymentSum'],
        ) for item in item_dict['data']['items']]
        return OrdersListDto(
            pages=item_dict['data']['pages'],
            items=items
        )
