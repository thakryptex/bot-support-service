from celery import shared_task

from apps.bot_user.models import BotUser
from logger import app_logger


@shared_task(bind=True, name='logout_all_bot_users')
def logout_all_bot_users(task):
    try:
        BotUser.objects.update(phone=None, token=None)
    except Exception as e:
        app_logger.exception(e)
