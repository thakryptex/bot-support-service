import logging
import os

import django
import telebot
from django.conf import settings

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
    django.setup()
    if settings.ENVIRONMENT != 'dev':
        logger = telebot.logger
        telebot.logger.setLevel(logging.DEBUG)
        from apps.bot_user.main import bot
        bot.polling(none_stop=True)
