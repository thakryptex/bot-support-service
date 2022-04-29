from atlas_utils.common.exceptions import Unauthorised
from django.db import transaction

from apps.bot_user.repository import BotRepository, NodeRepository
from apps.support.service import SupportService
from services.blinger.client import blinger_adapter
from services.order.client import order_adapter
from services.order.dto import OrderDto
from services.pyramid.client import pyramid_client
from utils.bot import BotStateStack
from utils.datetime import get_now_msk
from utils.db import paginate_queryset


class BotService:
    repository = BotRepository

    @classmethod
    def is_authorized(cls, tg_id):
        return cls.repository.is_authorized(tg_id=tg_id)

    @classmethod
    def is_herb(cls, tg_id):
        return cls.repository.is_herb(tg_id=tg_id)

    @classmethod
    def get_user(cls, tg_id):
        return cls.repository.get_user(tg_id=tg_id)

    @classmethod
    def get_or_create_user(cls, tg_user):
        user_id = tg_user.id
        first_name = tg_user.first_name
        last_name = tg_user.last_name
        name = " ".join(filter(None, [first_name, last_name]))
        username = tg_user.username
        return cls.repository.get_or_create_user(tg_id=user_id, name=name, username=username)

    @classmethod
    def update_user(cls, user_id, phone, **kwargs):
        cls.repository.update_user(user_id, phone, **kwargs)

    @classmethod
    def set_state(cls, user_id, state: str, additional_data: str = None):
        cls.repository.set_state(user_id, state)
        BotStateStack.state_stack_cache(user_id, state, additional_data)

    @classmethod
    def get_state(cls, user_id):
        return cls.repository.get_state(user_id)

    @classmethod
    def get_previous_state(cls, user_id):
        return cls.repository.get_previous_state(user_id)

    @classmethod
    def get_last_message(cls, user_id):
        return cls.repository.get_last_message(user_id)

    @classmethod
    def set_last_message(cls, user_id, message_id):
        return cls.repository.set_last_message(user_id, message_id)

    @classmethod
    def save_to_storage(cls, user_id, data, append=True) -> dict:
        return cls.repository.save_to_storage(user_id, data, append)

    @classmethod
    def get_storage(cls, user_id):
        return cls.repository.get_storage(user_id)

    @classmethod
    def update_storage_data(cls, storage, category_key, key, value, as_type):
        data = storage.get(category_key, {})

        if as_type == str:
            data[key] = value
        elif as_type == list:
            data_list = data.get(key, [])
            data_list.append(value)
            data[key] = data_list
        elif as_type == dict:
            data_dict = data.get(key, {})
            data_dict.update(value)
            data[key] = data_dict

        storage[category_key] = data
        return storage

    @classmethod
    def clear_storage(cls, user_id):
        BotStateStack.state_stack_clear(user_id)
        return cls.repository.save_to_storage(user_id, {}, False)

    @classmethod
    def logout(cls, user_id):
        return cls.repository.logout(user_id)

    @classmethod
    def storage_dict_from_order_dto(cls, dto):
        data = {
            'status_code': dto.status_code,
            'status_text': dto.status_text,
            'total': dto.total or 0,
        }
        if isinstance(dto, OrderDto):
            data.update({
                'guid': dto.guid,
                'payed': dto.payed or 0,
                'payment_type': dto.payment_type,
            })

        else:
            data.update({
                'id': dto.id,
                'user_name': dto.user_name,
                'promocode': dto.promocode,
            })
        return data

    @classmethod
    def get_orders_list(cls, tg_user, page):
        user, created = BotService.get_or_create_user(tg_user)
        token = user.token
        if not token:
            raise Unauthorised()
        if user.herb_id:
            dto = pyramid_client.get_orders_list(token, user.herb_id, page)
        else:
            dto = order_adapter.get_orders_list(token, page)
        now_str = get_now_msk().strftime('%H:%M:%S %d.%m.%Y')
        orders = {
            item.client_number: cls.storage_dict_from_order_dto(item)
            for item in dto.items
        }
        if orders:
            cls.save_to_storage(tg_user.id, {'orders': orders, 'updated_at': now_str}, append=True)
        return dto.pages, orders

    @classmethod
    def update_order_info(cls, user_id, order_guid, client_number, herb_id, token):
        if herb_id:
            dto = pyramid_client.get_order_info(token, herb_id, client_number)
        else:
            dto = order_adapter.get_order_info(order_guid)
        now_str = get_now_msk().strftime('%H:%M:%S %d.%m.%Y')
        storage = cls.get_storage(user_id)
        orders = storage.get('orders')
        order_data = cls.storage_dict_from_order_dto(dto)
        orders[dto.client_number] = order_data
        cls.save_to_storage(user_id, {'orders': orders, 'updated_at': now_str}, append=True)
        return order_data

    @classmethod
    def create_request_with_message(cls, tg_id, context, text, photo):
        storage = cls.get_storage(tg_id)
        request_id = storage.get('request_id')
        with transaction.atomic():
            if request_id is None:
                request = SupportService.create_support_request(tg_id, context, False)
                request_id = request.id
                cls.save_to_storage(tg_id, {'request_id': request_id})
            message = SupportService.add_question(request_id, text, photo)
            cls.send_to_blinger(tg_id, text, message.file.url if photo else None)

    @classmethod
    def add_message(cls, user_id, request_id, text, photo=None):
        with transaction.atomic():
            message = SupportService.add_question(request_id, text, photo)
            cls.send_to_blinger(user_id, text, message.file.url if photo else None)
            return message

    @classmethod
    def send_to_blinger(cls, tg_id, text, photo=None):
        user = cls.get_user(tg_id)
        blinger_adapter.send_message(tg_id, user.name, user.phone, text, photo)

    @classmethod
    def get_support_history(cls, tg_user_id, page):
        pages, req_list = SupportService.get_request_list(tg_user_id, page)
        labels = [{'id': request.id, 'text': f'№{request.id} из меню {request.theme}'} for request in req_list]
        return pages, labels

    @classmethod
    def get_order_info_text(cls, user_id, client_number):
        storage = cls.save_to_storage(user_id, {'current_order': client_number}, append=True)
        orders = storage.get('orders', {})
        updated_at = storage.get('updated_at')
        order_data = orders.get(client_number)
        txt_list = [f"*Заказ №{client_number}*"]
        if order_data:
            if order_data.get('user_name'):
                txt_list.append(f' ({order_data["user_name"]})')
            txt_list.append(f'\n*Статус:* {order_data["status_text"] or "пусто"}\n'
                            f'*Сумма заказа:* {order_data["total"]}р.')
            if order_data.get('payment_type') not in ['cash_delivery', None]:
                # в случае оплаты наличкой, у нас нет инфы о выкупе
                txt_list.append(f'\n*Оплачено:* {order_data["payed"]}р.')
            if order_data.get('promocode'):
                txt_list.append(f'\n*Промокод:* {order_data["promocode"]}')
            if updated_at:
                txt_list.append(f'\n_Последнее обновление в {updated_at}_')
        else:
            txt_list.append(f'\n_Что-то пошло не так. Сообщите о проблеме в поддержку, пожалуйста._')
        return ''.join(txt_list)

    @classmethod
    def is_faq_exists(cls):
        return cls.repository.is_faq_exists()

    @classmethod
    def get_faq_list(cls, page):
        qs = cls.repository.get_faq_list()
        pages, qs = paginate_queryset(qs, page)
        return pages, [{'id': faq.id, 'text': faq.question} for faq in qs]

    @classmethod
    def get_faq_object(cls, faq_id):
        return cls.repository.get_faq_object(faq_id)


class NodeService:
    repository = NodeRepository

    @classmethod
    def get_node_by_id(cls, node_id, get_child=False):
        return cls.repository.get_node_by_id(node_id, get_child)

    @classmethod
    def get_children(cls, node):
        return cls.repository.get_children(node)

    @classmethod
    def get_ancestors(cls, node_stack):
        return cls.repository.get_node_stack(node_stack)

    @classmethod
    def get_field_from_closest_ancestor(cls, node_ancestors, field):
        for a in reversed(node_ancestors):
            if getattr(a, field, False):
                return getattr(a, field)
