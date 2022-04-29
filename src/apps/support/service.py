from collections import defaultdict
from datetime import date

from apps.bot_user.states import StateSearcher
from apps.support.repository import SupportRepository
from logger import app_logger
from services.jira.client import jira_client
from utils.db import paginate_queryset
from utils.functions import deactivate_default_factory

monitor_map = {
    'request_count': 'Новых запросов',
    'user_count': 'Пользователей на неделе',
    'response_count': 'Кол-во ответов',
    'files_count': 'Кол-во фото'
}


class SupportService:
    repository = SupportRepository

    @classmethod
    def handle_blinger_webhook(cls, params):
        user_id = params['client_id']
        data_type = params['type']
        data = params['data']
        request = SupportService.get_last_request(tg_id=user_id)
        if data_type == 'text':
            SupportService.add_answer(request_id=request.id, is_auto=False, text=data)
        elif data_type == 'image':
            SupportService.add_answer(request_id=request.id, is_auto=False, file=data)
        else:
            app_logger.error(f'BlingerWebhookView message data FIX THIS: {data}')

    @classmethod
    def create_support_request(cls, tg_id, context, is_auto):
        return cls.repository.create_support_request(tg_id, context, is_auto)

    @classmethod
    def get_last_request(cls, tg_id):
        return cls.repository.get_last_request(tg_id)

    @classmethod
    def add_question(cls, request_id, text=None, file=None):
        return cls.repository.add_question(request_id, text, file)

    @classmethod
    def add_answer(cls, request_id, is_auto, text=None, file=None):
        return cls.repository.add_answer(request_id, is_auto, text, file)

    @classmethod
    def get_request_list(cls, tg_id, page=None):
        qs = cls.repository.get_request_list(tg_id)
        pages, issues = paginate_queryset(qs, page)
        return pages, qs

    @classmethod
    def get_messages(cls, tg_id, request_id):
        messages = cls.repository.get_messages(tg_id, request_id)
        msgs = []
        from_user = None
        for message in messages:
            if message.file:
                if from_user != message.from_user:
                    msgs.append({'text': f"{'*Вы' if message.from_user else '*Оператор'}:*", 'data': None})
                msgs.append({'text': '', 'data': message.file.url})
            else:
                if from_user == message.from_user:
                    msgs[len(msgs) - 1]['text'] += f'\n{message.text}'
                else:
                    msgs.append({
                        'text': f"{'*Вы' if message.from_user else '*Оператор'}:*\n{message.text}", 'data': None
                    })
            from_user = message.from_user
        return msgs

    @classmethod
    def mark_request_as_finished(cls, tg_id, request_id):
        return cls.repository.mark_request_as_finished(tg_id, request_id)

    @classmethod
    def save_warehouse_request(cls, message_id, user_id, request):
        return cls.repository.save_warehouse_request(message_id, user_id, request)

    @classmethod
    def get_warehouse_by_message_id(cls, message_id):
        return cls.repository.get_warehouse_by_message_id(message_id)

    @classmethod
    def save_warehouse_response(cls, wh_request, text, file):
        return cls.repository.save_warehouse_response(wh_request, text, file)

    @classmethod
    def create_issue(cls, issue_id, **kwargs):
        return cls.repository.create_issue(issue_id, **kwargs)

    @classmethod
    def update_issue(cls, issue_id, **kwargs):
        return cls.repository.update_issue(issue_id, **kwargs)

    @classmethod
    def get_unfinished_issues(cls):
        return cls.repository.get_unfinished_issues()

    @classmethod
    def update_issue_status(cls, issue_id):
        status_key = jira_client.get_issue_status(issue_id)
        is_done = (status_key == 'done')
        if is_done:
            cls.repository.update_issue(issue_id, is_done=True)
        return is_done

    @classmethod
    def get_issue_by_id(cls, incident_id):
        issue = cls.repository.get_issue_by_id(incident_id)
        if not issue:
            return {}
        is_done = cls.update_issue_status(issue.issue_id)
        return {
            'title': issue.issue_id,
            'description': issue.description,
            'status': 'Решён' if is_done else 'В работе',
        }

    @classmethod
    def get_bot_monitor(cls, date_end: date):
        data = cls.repository.get_bot_monitor(date_end)
        states = cls.repository.get_bot_states(date_end)
        verbose_states = []
        for state, value in states:
            verbose = StateSearcher.get(state)
            verbose = verbose.verbose_name if verbose else state
            verbose_states.append((verbose, value))
        data['states'] = verbose_states
        return data

    @classmethod
    def get_warehouse_monitoring(cls, date_start: date, date_end: date):
        data_list = cls.repository.get_warehouse_monitoring(date_start, date_end)
        data_list += cls.repository.get_warehouse_total(date_end)
        date_headers = []
        metrics = defaultdict(list)
        for d in data_list:
            if 'date' in d:
                date_headers.append(d.pop('date'))
            for k, v in d.items():
                translated = monitor_map.get(k, k)
                metrics[translated].append(v)
        deactivate_default_factory(metrics)
        return metrics, date_headers

    @classmethod
    def get_user_incidents(cls, user_id, page):
        issues = cls.repository.get_user_incidents(user_id)
        pages, issues = paginate_queryset(issues, page)
        return pages, issues

