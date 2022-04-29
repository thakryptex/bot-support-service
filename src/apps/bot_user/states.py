from utils.bot import BotState


class Init(BotState):
    name = 'init'
    verbose_name = 'Главное меню'


class Start(BotState):
    name = 'start'
    verbose_name = 'Авторизация'


class Confirm(BotState):
    name = 'confirm'
    verbose_name = 'Подтверждение'


class Question(BotState):
    name = 'question'
    verbose_name = 'Вопрос'


class Warehouse(BotState):
    name = 'warehouse'
    verbose_name = 'Фото со склада'


class Incident(BotState):
    name = 'incident'
    verbose_name = 'Инцидент'


class IncidentList(BotState):
    name = 'incident_list'
    verbose_name = 'Список инцидентов'


class IncidentInfo(BotState):
    name = 'incident_info'
    verbose_name = 'Информация по инциденту'


class OrderMenu(BotState):
    name = 'order_menu'
    verbose_name = 'Заказы'


class OrderInfo(BotState):
    name = 'order_info'
    verbose_name = 'Инфо о заказе'


class FaqMenu(BotState):
    name = 'faq_menu'
    verbose_name = 'ЧаВо'


class FaqInfo(BotState):
    name = 'faq_info'
    verbose_name = 'Вопрос-ответ'


class History(BotState):
    name = 'history'
    verbose_name = 'История обращений'


class HistoryRequest(BotState):
    name = 'history_request'
    verbose_name = 'Диалог обращения'


class StateSearcher:
    @classmethod
    def get(cls, state_name):
        parts = state_name.split('_')
        state_class_name = "".join([part.capitalize() for part in parts])
        state_class = globals().get(state_class_name)
        if state_class and issubclass(state_class, BotState):
            return state_class
