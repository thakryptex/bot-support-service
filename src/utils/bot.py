import json
import re
from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple, List, Union, Callable

import telebot
from django.core.cache import cache
from django.db import models
from telebot.apihelper import ApiException

from logger import app_logger


class BotWithMsgCacheWrapper(telebot.TeleBot):
    def delete_messages(self, chat_id, message_id, leave_last=False):
        try:
            msgs = self.get_msg_pull(chat_id)
            if msgs:

                for i, msg in enumerate(msgs, start=1):
                    if leave_last and i == len(msgs):
                        break
                    self.delete_message(chat_id, msg)
                if leave_last:
                    self.set_msg_pull(chat_id, msgs[-1])
                else:
                    self.clear_msg_pull(chat_id)
                return
        except Exception as e:
            app_logger.error(e)
        # в случае, если кэш упал, то можно из базы вытянуть последнее сообщение
        self.delete_message(chat_id, message_id)

    @staticmethod
    def set_msg_pull(chat_id, message_id):
        msg_cache_key = f'msg_pull_{chat_id}'
        cache.set(msg_cache_key, message_id)

    @staticmethod
    def append_msg_pull(chat_id, message_id):
        msg_cache_key = f'msg_pull_{chat_id}'
        msgs_str = cache.get(msg_cache_key, default='')
        msgs_str = f'{msgs_str},{message_id}' if msgs_str else str(message_id)
        cache.set(msg_cache_key, msgs_str)

    @staticmethod
    def clear_msg_pull(chat_id):
        msg_cache_key = f'msg_pull_{chat_id}'
        cache.delete(msg_cache_key)

    @staticmethod
    def get_msg_pull(chat_id):
        msg_cache_key = f'msg_pull_{chat_id}'
        msgs_str = cache.get(msg_cache_key, default='')
        return msgs_str.split(',')


class BotWrapper(BotWithMsgCacheWrapper):
    def __init__(self, token, service, threaded=True, skip_pending=False, num_threads=2):
        super().__init__(token, threaded, skip_pending, num_threads)
        self.service = service

    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode='Markdown', disable_notification=None, add_to_message_pull=True):
        try:
            sent_message = super().send_message(chat_id, text, disable_web_page_preview, reply_to_message_id,
                                                reply_markup,
                                                parse_mode,
                                                disable_notification)
            if add_to_message_pull:
                self.set_last_message(chat_id, sent_message.message_id)
            return sent_message
        except ApiException as e:
            print(e)

    def edit_message_text(self, text, chat_id=None, callback_id=None, message_id=None, inline_message_id=None,
                          parse_mode='Markdown', disable_web_page_preview=None, reply_markup=None):
        try:
            self.answer_callback_query(callback_id)
        except ApiException as e:
            print(e)
        return super().edit_message_text(text, chat_id, message_id, inline_message_id, parse_mode,
                                         disable_web_page_preview, reply_markup)

    def send_photo(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None,
                   parse_mode='Markdown', disable_notification=None, add_to_message_pull=True):
        try:
            sent_message = super().send_photo(chat_id, photo, caption, reply_to_message_id, reply_markup,
                                              parse_mode, disable_notification)
            if add_to_message_pull:
                self.set_last_message(chat_id, sent_message.message_id)
        except ApiException as e:
            print(e)

    def set_last_message(self, chat_id, message_id):
        self.service.set_last_message(chat_id, message_id)
        self.append_msg_pull(chat_id, message_id)

    def delete_message(self, chat_id, message_id):
        try:
            return super().delete_message(chat_id, message_id)
        except ApiException:
            return False

    def process_photo_from_message(self, message):
        photo = message.photo
        if photo:
            file_id = photo[-1].file_id
            file_info = self.get_file(file_id)
            photo = self.download_file(file_info.file_path)
        return photo


class AbstractStateModel(models.Model):
    class Meta:
        abstract = True
        verbose_name = 'Состояние'
        verbose_name_plural = 'Состояния'
        ordering = ['user', '-created_at']

    state = models.CharField(max_length=32, verbose_name='Состояние')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время переключения состояния')

    @property
    @abstractmethod
    def user(self):
        """Поле модели, описывающее связь с юзером"""
        pass


class BotState(metaclass=ABCMeta):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def verbose_name(self):
        pass


class BotStateStack:
    @classmethod
    def loads(cls, stack_str):
        try:
            stack = json.loads(stack_str)
        except (json.JSONDecodeError, TypeError) as e:
            app_logger.exception(e)
            stack = []
        return stack

    @classmethod
    def state_stack_cache(cls, user_id, state: str, additional_data: str = None):
        stack_key = f'state_stack_{user_id}'
        stack_str = cache.get(stack_key, default='[]')
        stack = cls.loads(stack_str)
        if not stack or stack[-1].get('state') != state or stack[-1].get('data') != additional_data:
            stack.append({'state': state, 'data': additional_data})
            cache.set(stack_key, json.dumps(stack))

    @classmethod
    def state_stack_pop(cls, user_id):
        stack_key = f'state_stack_{user_id}'
        stack_str = cache.get(stack_key, default='')
        if stack_str:
            stack = cls.loads(stack_str)
            if len(stack) > 1:
                stack.pop()
                cache.set(stack_key, json.dumps(stack))
                return stack[-1]
            else:
                cls.state_stack_clear(user_id)

    @classmethod
    def state_stack_clear(cls, user_id):
        stack_key = f'state_stack_{user_id}'
        cache.delete(stack_key)


class BotMessageHandler(metaclass=ABCMeta):
    def __init__(self, message, state):
        self.message = message
        self.state = state
        self.user_id = message.from_user.id
        self.is_text = hasattr(message, 'text')
        self.is_callback = hasattr(message, 'data')

    @abstractmethod
    def handle(self):
        raise NotImplementedError


class StateMachine:
    def __init__(self):
        self.common_callbacks = []
        self.callback_behavior = {}
        self.message_behavior = {}

    def set_common_callbacks(self, common: List[Tuple]):
        self.common_callbacks = common

    def set_callback_behavior(self, behavior: Dict[str, list]):
        self.callback_behavior = behavior

    def set_message_behavior(self, behavior: Dict[str, list]):
        self.message_behavior = behavior

    def get_output(self, state: str, input_string: str,
                   is_callback: bool) -> Union[Union[Callable, BotMessageHandler], bool]:
        if is_callback:
            transitions = self.common_callbacks
            transitions.extend(self.callback_behavior.get(state) or [])
        else:
            transitions = self.message_behavior.get(state)
        if transitions:
            for input, output in transitions:
                if re.search(input, input_string) is not None:
                    return output
        return False


def content_filter(types: list):
    def real_decorator(function):
        def wrapper(message, state):
            if message.content_type in types:
                function(message, state)
        return wrapper
    return real_decorator
