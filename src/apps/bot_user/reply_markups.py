from telebot import types

item_phone_required = types.KeyboardButton(text='Отправить Ваш текущий номер телефона', request_contact=True)

item_main = types.InlineKeyboardButton('⏮️ Вернуться в меню', callback_data="init")
item_go_back = types.InlineKeyboardButton('↩️ Назад', callback_data="return_to_previous")
item_faq = types.InlineKeyboardButton('♻️ Частые вопросы', callback_data="faq_menu")
item_question = types.InlineKeyboardButton('❓ Задать вопрос', callback_data="question")
item_warehouse = types.InlineKeyboardButton('📸 Запросить фото товара', callback_data="warehouse")
item_incident = types.InlineKeyboardButton('😠 Произошёл инцидент', callback_data="incident")
item_incident_status = types.InlineKeyboardButton('❓ Статус моих обращений', callback_data="incident_list")
item_logout = types.InlineKeyboardButton('👋🏻 Выйти из аккаунта', callback_data="logout")

item_orders = types.InlineKeyboardButton('🧾 Заказы', callback_data="order_menu")
item_items = types.InlineKeyboardButton('🛍 Инфо о товарах', callback_data="items_menu")
item_store = types.InlineKeyboardButton('🔐 Хранение', callback_data="store_menu")
item_delivery = types.InlineKeyboardButton('🚚 Доставка', callback_data="delivery_menu")

item_order_status = types.InlineKeyboardButton('Статус заказа', callback_data="order_status")
item_promocode = types.InlineKeyboardButton('Промокод', callback_data="promocode")
item_return = types.InlineKeyboardButton('Возврат', callback_data="return")

item_order_change = types.InlineKeyboardButton('Изменить заказ', callback_data="order_change")
item_order_cancel = types.InlineKeyboardButton('Отмена заказа', callback_data="order_cancel")
item_order_refresh = types.InlineKeyboardButton('Обновить статус', callback_data="order_refresh")
item_order_comment = types.InlineKeyboardButton('Комментарий к заказу', callback_data="order_comment")

item_item_info = types.InlineKeyboardButton('Инфо о товаре', callback_data="item_info")
item_item_avail = types.InlineKeyboardButton('Доступен ли на складе?', callback_data="item_avail")

item_store_time = types.InlineKeyboardButton('Срок хранения', callback_data="store_time")
item_store_prolong = types.InlineKeyboardButton('Продлить срок', callback_data="store_prolong")

item_done = types.InlineKeyboardButton('✅ Завершить', callback_data="Завершить")

item_yes = types.InlineKeyboardButton('✅ Да', callback_data="yes")
item_no = types.InlineKeyboardButton('❌ Нет', callback_data="no")

markup_hide = types.ReplyKeyboardRemove()

phone_required = types.ReplyKeyboardMarkup()
phone_required.row(item_phone_required)

yes_or_no = types.InlineKeyboardMarkup()
yes_or_no.row(item_yes, item_no)


def main(faq=False):
    main_menu = types.InlineKeyboardMarkup()
    main_menu.row(item_orders)
    if faq:
        main_menu.row(item_faq)
    main_menu.row(item_question)
    main_menu.row(item_warehouse)
    main_menu.row(item_incident)
    main_menu.row(item_logout)
    return main_menu


def apply_pagination(page, pages, markup):
    if 0 < page <= pages:
        btns = []
        first_page_on_screen = ((page - 1) // 5) * 5 + 1
        last_page_on_screen = min(first_page_on_screen + 4, pages)
        for i in range(first_page_on_screen, last_page_on_screen + 1):
            if i == first_page_on_screen and i > 1:
                btns.append(types.InlineKeyboardButton('<', callback_data=f"page_prev_{first_page_on_screen}"))
            text = f'•{i}•' if i == page else str(i)
            btns.append(types.InlineKeyboardButton(text, callback_data=f"page_{i}"))
            if i == last_page_on_screen and i < pages:
                btns.append(types.InlineKeyboardButton('>', callback_data=f"page_next_{last_page_on_screen}"))
        markup.row(*btns)


def get_order_keyboard(orders_list, pages, page):
    order_info = types.InlineKeyboardMarkup()
    for client_number, data in orders_list.items():
        user_name = data.get('user_name')
        if user_name:
            smile = order_status_smiles.get(data['status_code']) or '🆕'
            button_text = f'{smile} {client_number} ({user_name})'
        else:
            status_text = data['status_text'] or 'Статуса нет'
            button_text = f'{client_number} ({status_text})'
        button = types.InlineKeyboardButton(button_text, callback_data=f"order_id{client_number}")
        order_info.row(button)
    if pages > 1:
        apply_pagination(page, pages, order_info)
    order_info.row(item_main)
    return order_info


item_info = types.InlineKeyboardMarkup()
item_info.row(item_order_refresh)
item_info.row(item_question)
item_info.row(item_go_back, item_main)

question_and_history = types.InlineKeyboardMarkup()
question_and_history.row(item_main)


def get_paginated_keyboard(data_list, pages, page, callback_prefix, text_key='text', id_key='id'):
    markup = types.InlineKeyboardMarkup()
    for btn_data in data_list:
        button = types.InlineKeyboardButton(btn_data[text_key], callback_data=f"{callback_prefix}{btn_data[id_key]}")
        markup.row(button)
    if pages > 1:
        apply_pagination(page, pages, markup)
    markup.row(item_main)
    return markup


support_chat = types.InlineKeyboardMarkup()
support_chat.row(item_go_back, item_main)

store = types.InlineKeyboardMarkup()
store.row(item_store_time)
store.row(item_store_prolong)
store.row(item_question)
store.row(item_main)

return_to_main = types.InlineKeyboardMarkup()
return_to_main.row(item_main)

go_back_markup = types.InlineKeyboardMarkup()
go_back_markup.row(item_go_back)

back_and_main = types.InlineKeyboardMarkup()
back_and_main.row(item_go_back, item_main)

done = types.InlineKeyboardMarkup()
done.row(item_done)


def get_custom_keyboard():
    return types.InlineKeyboardMarkup()


def get_key_button(button_text, button_id):
    return types.InlineKeyboardButton(button_text, callback_data=button_id)


def go_to_support(request_id):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('Перейти к диалогу', callback_data=f"request_id{request_id}")
    markup.row(button)
    return markup


order_status_smiles = {
    'New': '🆕',
    'Exported': '⚙️',
    'Delivering': '🚛',
    'OnClient': '🤝',
    'OnPickupPoint': '🕒',
    'Canceled': '❌',
    'Returned': '🚫',
    'PartialPurchase': '💵',
    'WaitingForCancellation': '❌',
    'RETURN_REC': '🚫',
}
