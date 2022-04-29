import re
from logging import getLogger

from atlas_utils.common.exceptions import Unauthorised
from django.conf import settings
from telebot.apihelper import ApiException

from apps.bot_user import reply_markups as markups
from apps.bot_user.constants import full_warehouse_text
from apps.bot_user.reply_markups import phone_required, yes_or_no, markup_hide, get_custom_keyboard, get_key_button, \
    item_main, item_incident_status
from apps.bot_user.service import BotService, NodeService
from apps.bot_user.states import Init, Start, Confirm, OrderMenu, Question, StateSearcher, OrderInfo, Warehouse, \
    Incident, IncidentList, IncidentInfo
from apps.support.service import SupportService
from services.jira.client import jira_client
from services.jira.factory import JiraIssueFactory
from services.lobster.client import lobster_client
from services.pyramid.client import pyramid_client
from utils.bot import content_filter, BotWrapper, BotStateStack, BotMessageHandler
from utils.functions import remove_redundant_symbols

logger = getLogger(__name__)

bot = BotWrapper(settings.TG_TOKEN_SUPPORT_BOT, service=BotService)

auth_exclusion_ids = [666]  # id суперюзеров, можно сказать :)


# group handlers
def warehouse_reply(message):
    wh_req = SupportService.get_warehouse_by_message_id(message.reply_to_message.message_id)
    if wh_req:
        user_id = wh_req.user_id
        text = message.text or message.caption
        photo = bot.process_photo_from_message(message)
        SupportService.save_warehouse_response(wh_req, text=text, file=photo)

        reply_text = f'Ваш запрос:\n{wh_req.request}'
        if text:
            reply_text += f'\n\nОтвет склада:\n{text}'

        if photo:
            reply_text += f'\n\n_Пожалуйста, добавьте фотографию на сайт в отзывы о товаре._'
            bot.send_photo(user_id, photo, caption=reply_text, add_to_message_pull=False)
        else:
            bot.send_message(user_id, reply_text, add_to_message_pull=False)

        bot.send_message(message.chat.id, 'Доставлено', reply_to_message_id=message.message_id)
    else:
        bot.send_message(message.chat.id, 'Ответ не удалось доставить клиенту')


# private chat handlers
def start(message, state=None):
    user, created = BotService.get_or_create_user(message.from_user)
    if hasattr(message, 'data'):
        bot.answer_callback_query(message.id)
        message_id = BotService.get_last_message(message.from_user.id)
        edit_message_reply_markup(message.from_user.id, message_id)
    if created or not user.phone or not user.token:
        BotService.set_state(user.tg_id, Start.name)
        bot.send_message(message.from_user.id,
                         "Вас приветствует бот-помощник интернет-магазина Ennergiia.\n"
                         "Для того, чтобы продолжить работу с ботом необходимо авторизоваться. Отправьте боту *ваш "
                         "контакт*, под которым Вы оформляли последние заказы на сайте Ennergiia.",
                         reply_markup=phone_required)
    else:
        message_id = BotService.get_last_message(message.from_user.id)
        edit_message_reply_markup(message.from_user.id, message_id)
        init(message, 'init')


@content_filter(types=['text', 'contact'])
def confirm(message, state):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name  # required
    last_name = message.from_user.last_name  # optional
    name = f'{last_name or ""} {first_name}'.strip()
    phone = None
    if message.content_type == 'contact' and message.contact.user_id == user_id:
        phone = message.contact.phone_number
    elif user_id in auth_exclusion_ids:
        # допускает ввод телефона с помощью текста для узкого круга лиц
        text = message.text
        text = re.sub('[-() ]', '', text)
        phone_regex = r'^(?:\+?)?[78]\d{10,11}$'
        found = re.findall(phone_regex, text)
        phone = found[0] if found else None
    if phone:
        if phone.startswith('+'):
            phone = phone[1:]
        elif phone.startswith('8'):
            phone = '7' + phone[1:]
        BotService.set_state(user_id, Confirm.name)
        data_to_store = {'phone': phone, 'name': name, 'username': username}
        BotService.save_to_storage(user_id, data_to_store, append=False)
        bot.send_message(message.chat.id, 'Принято', reply_markup=markup_hide)
        bot.send_message(message.chat.id,
                         f"Убедитесь, что Вы ввели правильный номер: *+{phone}*?",
                         reply_markup=yes_or_no)
    else:
        bot.send_message(message.chat.id,
                         'Отправьте номер с помощью кнопки "Отправить Ваш текущий номер телефона".',
                         reply_markup=phone_required)


def auth(message, state):
    user_id = message.from_user.id
    storage_data = BotService.get_storage(user_id)
    phone = storage_data.get('phone')
    if not phone:
        bot.send_message(user_id, 'Похоже, что у Вас не указан телефон.')
        return start(message)
    try:
        token = lobster_client.check_auth_and_get_token(phone)
        herb_dto = pyramid_client.is_herb_user(token)
    except Exception as e:
        bot.send_message(user_id, 'Произошла ошибка при попытке авторизации. Попробуйте попозже.')
        return start(message)
    name = storage_data.get('name')
    username = storage_data.get('username')
    herb_id = herb_dto.id if herb_dto and not herb_dto.blocked else None
    BotService.update_user(user_id, phone, name=name, username=username, token=token, herb_id=herb_id)
    init(message, state)


def init(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, Init.name)
    BotService.clear_storage(user_id)
    is_herb = BotService.is_herb(user_id)
    msg_text = f"*Главное меню {'Гербота' if is_herb else 'Энергобота'}.*\n" \
               f"Здесь вы можете выбрать категорию вашего вопроса и получить автоматический ответ, либо от нашего " \
               f"менеджера, при этом не потеряв его в каком-либо чате поддержки. Если вы не нашли среди вариантов " \
               f"нужный вам, напишите напрямую через функцию 'Задать вопрос'."
    message_id = BotService.get_last_message(message.from_user.id)
    bot.delete_messages(user_id, message_id, leave_last=True)
    faq = BotService.is_faq_exists()
    if hasattr(message, 'data'):
        bot.edit_message_text(msg_text, user_id, message.id, message.message.message_id,
                              reply_markup=markups.main(faq))
    else:
        bot.send_message(user_id, msg_text, reply_markup=markups.main(faq))


def order_menu(message, state, page=1):
    tg_user = message.from_user
    BotService.set_state(tg_user.id, OrderMenu.name, additional_data=f'page_{page}')
    try:
        pages, orders_list = BotService.get_orders_list(tg_user, page)
    except Unauthorised:
        return auth(message, state)
    except Exception as e:
        logger.exception(e)
        bot.send_message(message.from_user.id, 'Возникла ошибка сервиса, либо вам нужно выйти из аккаунта '
                                               'и повторно авторизоваться.', add_to_message_pull=False)
        return init(message, state)

    if len(orders_list) > 0:
        text = "*Ваша история заказов.*\nПолучите более подробную информацию по одному из заказов, нажав на него.\n" \
               "Если ваших заказов больше, чем их влезает на страницу, вы можете воспользоваться навигацией внизу."
    else:
        text = "*Вы ещё не совершали заказов.*\nОформите заказ на [сайте](https://www.ennergiia.com/)."
    bot.edit_message_text(text, tg_user.id, message.id, message.message.message_id,
                          reply_markup=markups.get_order_keyboard(orders_list, pages, page))


def order_info(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, OrderInfo.name, additional_data=message.data)
    client_number = message.data.replace('order_id', '')
    order_refresh(message, state, client_number)


def order_refresh(message, state, client_number=None):
    user_id = message.from_user.id
    storage = BotService.get_storage(user_id)
    if not client_number:
        client_number = storage['current_order']
    orders = storage.get('orders')
    order_guid = orders[client_number].get('guid')
    user = BotService.get_user(user_id)
    token = user.token if user else None
    herb_id = user.herb_id if user else None
    if herb_id and not token:
        return auth(message, state)
    BotService.update_order_info(user_id, order_guid, client_number, herb_id, token)

    text = BotService.get_order_info_text(user_id, client_number)
    bot.edit_message_text(text, user_id, message.id, message.message.message_id,
                          reply_markup=markups.item_info)


def faq_menu(message, state, page=1):
    tg_user = message.from_user
    BotService.set_state(tg_user.id, 'faq_menu', additional_data=f'page_{page}')
    pages, faq_list = BotService.get_faq_list(page)
    if len(faq_list) > 0:
        text = "*Список часто задаваемых вопросов.*"
    else:
        text = "*Список вопросов пуст.*"
    bot.edit_message_text(text, tg_user.id, message.id, message.message.message_id,
                          reply_markup=markups.get_paginated_keyboard(faq_list, pages, page, 'faq_id'))


def faq_info(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, 'faq_info', additional_data=message.data)
    faq_id = message.data.replace('faq_id', '')
    faq = BotService.get_faq_object(faq_id)
    if faq:
        text = f'*{faq.question}*\n{faq.answer}'
    else:
        text = 'Такого вопрос-ответ не существует.'
    bot.edit_message_text(text, user_id, message.id, message.message.message_id, reply_markup=markups.back_and_main)


def question(message, state):
    user_id = message.from_user.id

    # проверяем на наличие реквестов, если есть, то сразу в реквест кидаем
    request = SupportService.get_last_request(user_id)
    if request:
        message.data = f'request_id{request.id}'
        return history_request(message, state)

    BotService.set_state(user_id, Question.name)
    bot.edit_message_text("*Не нашли ответ на свой вопрос? Задайте его нам прямо здесь, и мы вам ответим здесь же.*",
                          user_id, message.id, message.message.message_id, reply_markup=markups.question_and_history)


def history_request(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, 'history_request')
    request_id = message.data.replace('request_id', '')
    message_id = BotService.get_last_message(message.from_user.id)
    bot.delete_messages(user_id, message_id)
    bot.answer_callback_query(message.id)
    storage = BotService.save_to_storage(user_id, {'request_id': request_id})
    messages = SupportService.get_messages(user_id, request_id)
    bot.send_message(message.from_user.id, '*ИСТОРИЯ ПЕРЕПИСКИ*')
    for msg in messages:
        if msg['data']:
            bot.send_photo(message.from_user.id, msg['data'], caption=msg['text'])
        else:
            bot.send_message(message.from_user.id, msg['text'])

    text = "(_Вы можете продолжить диалог, отправив новое сообщение_)"
    client_number = storage.get('current_order')
    if client_number:
        text = f'Вы перешли сюда из заказа *{client_number}*\n' + text
    bot.send_message(message.from_user.id, text, reply_markup=markups.support_chat)


@content_filter(types=['text', 'photo'])
def add_question(message, state):
    user_id = message.from_user.id
    message_id = BotService.get_last_message(user_id)
    bot.delete_messages(user_id, message_id)
    text = message.text or message.caption
    photo = bot.process_photo_from_message(message)

    # получение текстового описания предыдущего стейта
    prev_state = BotService.get_previous_state(user_id)
    state_class = StateSearcher.get(prev_state.state) or Question
    BotService.create_request_with_message(user_id, state_class.verbose_name, text=text, photo=photo)
    bot.send_message(user_id,
                     "Вопрос добавлен.\n"
                     "Если Вы его описали до конца, то нажмите кнопку '*Завершить*'.", reply_markup=markups.done)


@content_filter(types=['text', 'photo'])
def continue_dialog(message, state):
    user_id = message.from_user.id
    message_id = BotService.get_last_message(user_id)
    bot.delete_messages(user_id, message_id)
    text = message.text or message.caption
    photo = bot.process_photo_from_message(message)

    storage = BotService.get_storage(user_id)
    request_id = storage.get('request_id')
    if text:
        BotService.add_message(user_id, request_id, text=text, photo=None)
    if photo:
        BotService.add_message(user_id, request_id, text=None, photo=photo)
    bot.send_message(message.from_user.id,
                     "Сообщение добавлено.\n"
                     "Если Вы его описали до конца, то нажмите кнопку '*Завершить*'.", reply_markup=markups.done)


def warehouse(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, Warehouse.name)
    bot.edit_message_text("*Запросить фото товара со склада*\nПришлите, пожалуйста, артикул товара (например, 9070868) "
                          "или ссылку на товар, уточнив цвет и размер.",
                          user_id, message.id, message.message.message_id, reply_markup=markups.return_to_main)


@content_filter(types=['text'])
def send_to_warehouse(message, state):
    user_id = message.from_user.id
    message_id = BotService.get_last_message(user_id)
    bot.delete_messages(user_id, message_id)

    text = message.text

    user = BotService.get_user(user_id)
    sent = bot.send_message(settings.TG_WAREHOUSE_CHAT, f"*{full_warehouse_text(user.phone)}:*\n{text}")
    SupportService.save_warehouse_request(sent.message_id, user_id, text)

    bot.send_message(user_id,
                     "Запрос отправлен. Вам придёт уведомление как фотографии будут готовы.\n"
                     "Если нужно запросить фото по другому артикулу, то можете отправить ещё.\n"
                     "Когда закончите, нажмите кнопку '*Завершить*'.", reply_markup=markups.done)


def incident(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, Incident.name)

    node = NodeService.get_node_by_id(Incident.name)
    if not node:
        bot.send_message(user_id, "Данный подпункт меню недоступен.")
        return init(message, state)

    keyboard = get_custom_keyboard()
    children = NodeService.get_children(node)
    for child in children:
        keyboard.row(get_key_button(child.button_name, child.node_id))
    keyboard.row(item_incident_status)
    keyboard.row(item_main)

    bot.edit_message_text("*Сообщить об инциденте*\nС чем возникла проблема?",
                          user_id, message.id, message.message.message_id, reply_markup=keyboard)


def incident_list(message, state, page=1):
    user_id = message.from_user.id
    BotService.set_state(user_id, IncidentList.name, additional_data=f'page_{page}')
    pages, issues = SupportService.get_user_incidents(user_id, page)
    if not issues:
        bot.edit_message_text(
            "*Список ваших обращений по инцидентам пуст.*\nЛибо вы их не создавали ранее, либо они уже все решены.",
            user_id, message.id, message.message.message_id, reply_markup=markups.return_to_main)
    else:
        for issue in issues:
            if issue['is_done']:
                emoji = '✅ '
            else:
                emoji = '⚙ '
            issue['issue_id'] = emoji + issue['issue_id']
        bot.edit_message_text(
            "*Список ваших обращений по инцидентам*\nВы можете получить статус решения инцидента, посмотреть детали.\n"
            "✅ - проблема решена, ⚙ - в работе.",
            user_id, message.id, message.message.message_id,
            reply_markup=markups.get_paginated_keyboard(issues, pages, page, 'incident_id', 'issue_id')
        )


def incident_info(message, state):
    user_id = message.from_user.id
    BotService.set_state(user_id, IncidentInfo.name, additional_data=message.data)
    incident_id = message.data.replace('incident_id', '')
    issue_data = SupportService.get_issue_by_id(incident_id)
    if issue_data:
        text = f"*{issue_data['title']}*\nСтатус: {issue_data['status']}\n\nОписание:\n{issue_data['description']}"
    else:
        text = 'Такого инцидента не существует.'
    bot.edit_message_text(text, user_id, message.id, message.message.message_id, reply_markup=markups.back_and_main)


class NodeHandler(BotMessageHandler):
    def __init__(self, message, state):
        super().__init__(message, state)
        self.storage = BotService.get_storage(self.user_id)
        self.storage_updated = False
        self.node_storage_key = 'node_data'
        self.node_stack_key = 'stack'
        self.node_answer_key = 'answers'
        self.keyboard = markups.get_custom_keyboard()
        self.node = None
        self.__children = None

    def handle(self):
        self.check_validity()
        self.process_node()
        if self.node_has_children():
            success = self.process_descendants()
        else:
            success = self.finish_chain()
        self.update_storage()
        self.send_answer(success)

    def check_validity(self):
        if self.is_callback:
            node_id = self.message.data
        else:
            node_stack = self.storage.get(self.node_storage_key, {}).get(self.node_stack_key, [])
            node_id = node_stack[-1] if node_stack else None
        self.node = NodeService.get_node_by_id(node_id, get_child=self.is_text)
        if not self.node:
            bot.send_message(self.user_id, "Данный подпункт меню недоступен.")
            return incident(self.message, self.state)

    def process_node(self):
        if self.is_text:
            user_answer = f'В: {self.node.parent.title}\nО: {self.message.text}'
            self.storage = BotService.update_storage_data(self.storage, self.node_storage_key, self.node_answer_key,
                                                          user_answer, list)

        self.storage = BotService.update_storage_data(
            self.storage, self.node_storage_key, self.node_stack_key, self.node.node_id, list)
        self.storage_updated = True

    def __get_children(self):
        self.__children = NodeService.get_children(self.node)
        return self.__children

    @property
    def children(self):
        return self.__children or self.__get_children()

    def node_has_children(self):
        return bool(self.children)

    def process_descendants(self):
        for child in self.children:
            if child.input_waiting:
                break
            else:
                button = markups.get_key_button(child.button_name, child.node_id)
                self.keyboard.row(button)
        return True

    def finish_chain(self):
        try:
            issue_data = self.get_issue_data()
            issue_dto = JiraIssueFactory.dto_from_dict(issue_data)
            issue_key = jira_client.create_issue(issue_dto)
            SupportService.create_issue(
                issue_key, user_id=self.user_id, title=issue_data['title'], description=issue_data['description']
            )
        except Exception as e:
            logger.error(e)
            return False
        return True

    def get_issue_data(self):
        db_user = BotService.get_user(self.user_id)

        node_data = self.storage.get(self.node_storage_key, {})
        node_stack = node_data.get(self.node_stack_key, [])
        ancestors = NodeService.get_ancestors(node_stack)

        issue_title = [remove_redundant_symbols(a.button_name) for a in ancestors if not a.input_waiting]
        issue_title = ', '.join(issue_title).capitalize() + f' ({db_user.phone})'

        desc = f'Пользователь {db_user.phone}:\n\n' + '\n\n'.join(node_data.get(self.node_answer_key, []))

        issue_type = NodeService.get_field_from_closest_ancestor(ancestors, 'issue_type') or '10005'
        assignee = NodeService.get_field_from_closest_ancestor(ancestors, 'assignee')
        assignee = assignee.jira_id if assignee else '60099fcfe2a13500697dcd17'

        return {'title': issue_title, 'description': desc, 'issue_type': issue_type, 'assignee': assignee}

    def update_storage(self):
        if self.storage_updated:
            self.storage = BotService.save_to_storage(self.user_id, self.storage)

    def send_answer(self, success=True):
        if success:
            self.keyboard.row(item_main)
            message_text = f'*{self.node.title}*\n{self.node.description if self.node.description else ""}'
            if hasattr(self.message, 'data'):
                bot.edit_message_text(message_text, self.user_id, self.message.id, self.message.message.message_id,
                                      reply_markup=self.keyboard)
            else:
                bot.send_message(self.user_id, message_text, reply_markup=self.keyboard)
        else:
            bot.send_message(self.user_id, 'Ошибка при создании инцидента. Попробуйте попозже.',
                             reply_markup=markups.return_to_main)


def done(message, state):
    if state == 'question':
        # проверять контекст вызова и возвращать в меню вызова, не только в главное
        BotService.set_state(message.from_user.id, Init.name)
        init(message, state)


def logout(message, state):
    BotService.logout(message.from_user.id)
    message_id = BotService.get_last_message(message.from_user.id)
    edit_message_reply_markup(message.from_user.id, message_id)
    start(message, state)


def return_to_previous(message, state):
    user_id = message.from_user.id
    prev_state = BotStateStack.state_stack_pop(user_id)
    if not prev_state:
        return init(message, state)
    function_name = prev_state['state']
    data = prev_state['data']
    paginated = data.startswith('page_') if data else False
    message_id = BotService.get_last_message(user_id)
    bot.delete_messages(user_id, message_id, leave_last=True)
    if data and not paginated:
        message.data = data
    if paginated:
        page = int(data.split('_')[-1])
        globals()[function_name](message, state, page)
    else:
        globals()[function_name](message, state)


def page_handler(message, state):
    try:
        page = int(message.data.replace('page_', ''))
    except Exception:
        page = 1
    globals()[state](message, state, page)


def page_prev(message, state):
    try:
        page = int(message.data.replace('page_prev_', ''))
    except Exception:
        page = 2
    globals()[state](message, state, page - 1)


def page_next(message, state):
    try:
        page = int(message.data.replace('page_next_', ''))
    except Exception:
        page = 0
    globals()[state](message, state, page + 1)


def edit_message_reply_markup(chat_id=None, message_id=None, inline_message_id=None, reply_markup=None):
    try:
        bot.edit_message_reply_markup(chat_id, message_id, inline_message_id, reply_markup)
    except ApiException as e:
        print(e)


def notify_user(message):
    user_id = message.request.bot_user_id
    offline_bot = BotWrapper(settings.TG_TOKEN_SUPPORT_BOT, service=BotService)
    offline_bot.send_message(user_id, f'Оператор ответил по вашему запросу:\n{message.text or "файл"}',
                             reply_markup=markups.go_to_support(message.request_id))
