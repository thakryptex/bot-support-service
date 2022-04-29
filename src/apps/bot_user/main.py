from logging import getLogger

from django.conf import settings
from django.db import transaction

from apps.bot_user.constants import warehouse_text
from apps.bot_user.handlers import bot, start, warehouse_reply
from apps.bot_user.routes import state_machine
from apps.bot_user.service import BotService
from apps.bot_user.states import Start, Confirm
from utils.decorators import handle_exceptions

logger = getLogger(__name__)


@handle_exceptions
@bot.message_handler(func=lambda message: message.chat.type != "private", content_types=['text', 'photo'])
def group_handler(message):
    reply = message.reply_to_message
    if reply and str(reply.from_user.id) == settings.TG_SUPPORT_BOT_ID:
        if warehouse_text in reply.text:
            warehouse_reply(message)


@handle_exceptions
@bot.message_handler(commands=['start'], func=lambda message: message.chat.type == "private")
def start_handler(message):
    start(message)


@handle_exceptions
@bot.callback_query_handler(func=lambda message: True)
@bot.message_handler(func=lambda message: message.chat.type == "private", content_types=['text', 'contact', 'photo'])
def main_handler(message):
    state = BotService.get_state(message.from_user.id)
    state = state.state if state else 'init'
    if state not in [Start.name, Confirm.name] and not BotService.is_authorized(message.from_user.id):
        return start(message)
    input_string, is_callback = (message.data, True) if hasattr(message, 'data') else (message.text, False)
    if input_string is None:  # true for contacts
        input_string = '.'
    handler = state_machine.get_output(state, input_string, is_callback)
    if handler:
        with transaction.atomic():
            if hasattr(handler, 'handle'):
                handler(message, state).handle()
            else:
                handler(message, state)
    else:
        start(message)  # just restart?


@handle_exceptions
@bot.message_handler(content_types=['audio', 'document', 'sticker', 'video', 'video_note', 'voice', 'location'])
def other_contents(message):
    bot.send_message(
        message.chat.id,
        f"Данный формат сообщений не поддерживается. Следуйте инструкциям в меню бота.\n"
        f"В чате с техподдержкой доступны только текстовые и фотосообщения.\n"
        f"Если же ничего не работает, нажмите снова /start."
    )
