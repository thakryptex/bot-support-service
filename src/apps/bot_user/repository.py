from django.db.models import Q

from apps.bot_user.models import BotUser, State, Storage, FAQ, MenuNode


class BotRepository:

    @classmethod
    def is_authorized(cls, tg_id):
        return BotUser.objects.filter(tg_id=tg_id, phone__isnull=False, token__isnull=False).exists()

    @classmethod
    def is_herb(cls, tg_id):
        return BotUser.objects.filter(tg_id=tg_id, herb_id__isnull=False).exists()

    @classmethod
    def get_user(cls, tg_id: int):
        return BotUser.objects.filter(tg_id=tg_id).first()

    @classmethod
    def get_or_create_user(cls, tg_id: int, name: str, **kwargs):
        defaults = {'name': name}.update(kwargs)
        return BotUser.objects.get_or_create(tg_id=tg_id, defaults=defaults)

    @classmethod
    def update_user(cls, tg_id: int, phone: str, **kwargs):
        kwargs['phone'] = phone
        BotUser.objects.filter(tg_id=tg_id).update(**kwargs)

    @classmethod
    def get_state(cls, tg_id: int):
        return State.objects.filter(user_id=tg_id).first()

    @classmethod
    def set_state(cls, tg_id: int, state: str):
        State.objects.create(user_id=tg_id, state=state)

    @classmethod
    def get_previous_state(cls, tg_id: int):
        qs = State.objects.filter(user_id=tg_id).all()
        if qs.count() > 1:
            return qs[1]
        return

    @classmethod
    def get_last_message(cls, tg_id: int):
        last_message = BotUser.objects.filter(tg_id=tg_id).values_list('last_message', flat=True)
        return last_message[0] if len(last_message) > 0 else None

    @classmethod
    def set_last_message(cls, tg_id: int, message_id: int):
        return BotUser.objects.filter(tg_id=tg_id).update(last_message=message_id)

    @classmethod
    def save_to_storage(cls, tg_id: int, data: dict, append=True) -> dict:
        if append:
            storage, created = Storage.objects.get_or_create(user_id=tg_id)
            storage.data.update(data)
            storage.save()
        else:
            storage, created = Storage.objects.update_or_create(user_id=tg_id, defaults={'data': data})
        return storage.data

    @classmethod
    def get_storage(cls, tg_id: int) -> dict:
        storage = Storage.objects.filter(user_id=tg_id).first()
        if storage:
            return storage.data
        return {}

    @classmethod
    def logout(cls, user_id):
        return BotUser.objects.filter(tg_id=user_id).update(token=None)

    @classmethod
    def is_faq_exists(cls):
        return FAQ.objects.exists()

    @classmethod
    def get_faq_list(cls):
        return FAQ.objects.all()

    @classmethod
    def get_faq_object(cls, faq_id):
        return FAQ.objects.filter(id=faq_id).first()


class NodeRepository:
    @classmethod
    def get_node_by_id(cls, node_id, get_child=False):
        if get_child:
            lookup = Q(parent__node_id=node_id) | Q(parents__node_id=node_id)
        else:
            lookup = Q(node_id=node_id)
        return MenuNode.objects.filter(lookup).first()

    @classmethod
    def get_children(cls, node):
        return node.get_children() or node.children_m2m.all()

    @classmethod
    def get_node_stack(cls, node_ids):
        return MenuNode.objects.filter(node_id__in=node_ids).order_by('level').all()
