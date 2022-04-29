from datetime import date, timedelta

from cloudinary.uploader import upload_resource
from django.db import connection
from django.db.models import Q

from apps.support.models import SupportRequest, Message, WarehouseRequest, WarehouseResponse, Issue
from utils.datetime import get_now_msk
from utils.db import dictfetchall


class SupportRepository:

    @classmethod
    def create_support_request(cls, tg_id, context, is_auto):
        return SupportRequest.objects.create(bot_user_id=tg_id, theme=context, is_done=is_auto)

    @classmethod
    def __create_message(cls, request_id, is_auto, from_user, text, file):
        if not text and not file:
            raise Exception('Хрень')
        if file:
            file = upload_resource(file, folder='herb_bot')
        return Message.objects.create(request_id=request_id, is_auto=is_auto, from_user=from_user,
                                      text=text, file=file)

    @classmethod
    def get_last_request(cls, tg_id):
        return SupportRequest.objects.filter(bot_user_id=tg_id).order_by('-messages__created_at').first()

    @classmethod
    def add_question(cls, request_id, text=None, file=None):
        return cls.__create_message(request_id, False, True, text, file)

    @classmethod
    def add_answer(cls, request_id, is_auto, text=None, file=None):
        return cls.__create_message(request_id, is_auto, False, text, file)

    @classmethod
    def get_request_list(cls, tg_id):
        return SupportRequest.objects.filter(bot_user_id=tg_id, is_done=False).order_by('-id').all()

    @classmethod
    def get_messages(cls, tg_id, request_id, limit=20):
        return Message.objects.filter(
            request__bot_user_id=tg_id, request_id=request_id
        ).order_by('-created_at').all()[:limit:-1]

    @classmethod
    def mark_request_as_finished(cls, tg_id, request_id):
        return SupportRequest.objects.filter(bot_user_id=tg_id, id=request_id).update(is_done=True)

    @classmethod
    def save_warehouse_request(cls, message_id, user_id, request):
        return WarehouseRequest.objects.update_or_create(message_id=message_id, user_id=user_id,
                                                         defaults={'request': request})

    @classmethod
    def get_warehouse_by_message_id(cls, message_id) -> WarehouseRequest:
        return WarehouseRequest.objects.filter(message_id=message_id).first()

    @classmethod
    def save_warehouse_response(cls, wh_request, text, file):
        if not text and not file:
            raise Exception('Хрень')
        if file:
            file = upload_resource(file, folder='warehouse')
        return WarehouseResponse.objects.create(request=wh_request, text=text, file=file)

    @classmethod
    def create_issue(cls, issue_id, **kwargs):
        return Issue.objects.update_or_create(issue_id=issue_id, defaults=kwargs)

    @classmethod
    def update_issue(cls, issue_id, **kwargs):
        return Issue.objects.filter(issue_id=issue_id).update(**kwargs)

    @classmethod
    def get_unfinished_issues(cls):
        return Issue.objects.filter(is_done=False).values_list('issue_id', flat=True)

    @classmethod
    def get_issue_by_id(cls, incident_id):
        return Issue.objects.filter(id=incident_id).first()

    @classmethod
    def get_bot_monitor(cls, date_end: date):
        query = """
            with users as (
                select count(*) users
                from bot_user_botuser
                where created_at >= '2020-03-01' and created_at <= %(date_end)s::date
            ), auth as (
                select count(*) auth
                from bot_user_botuser
                where phone is not null and created_at <= %(date_end)s::date
            ), nonherb as (
                select count(*) nonherb
                from bot_user_botuser
                where token is not null and herb_id is null and created_at <= %(date_end)s::date
            ), msgs as (
                select count(*) msgs
                from support_message
                where request_id not in (2, 3, 4) and created_at <= %(date_end)s::date
            ), auto_msgs as (
                select count(*) auto_msgs
                from support_message
                where request_id not in (2, 3, 4) and text like '%%Вы написали в поддержку компании ennergiia%%' and created_at <= %(date_end)s
            ), user_msgs as (
                select count(*) user_msgs
                from support_message
                where request_id not in (2, 3, 4) and from_user and created_at <= %(date_end)s::date
            ), manager_msgs as (
                select count(*) manager_msgs
                from support_message
                where request_id not in (2, 3, 4) and not from_user and created_at <= %(date_end)s::date
            )

            select
                coalesce(users, 0) users,
                coalesce(auth, 0) auth,
                coalesce(nonherb, 0) nonherb,
                coalesce(msgs, 0) msgs,
                coalesce(auto_msgs, 0) auto_msgs,
                coalesce(user_msgs, 0) user_msgs,
                coalesce(manager_msgs, 0) manager_msgs
            from users
            cross join auth
            cross join nonherb
            cross join msgs
            cross join auto_msgs
            cross join user_msgs
            cross join manager_msgs
            """
        with connection.cursor() as cursor:
            cursor.execute(query, {'date_end': date_end})
            data = dictfetchall(cursor)
            return data[0]

    @classmethod
    def get_bot_states(cls, date_end: date):
        query = """
            select state, count(id)
            from bot_user_state
            where user_id not in (120106597, 786620157, 53215507, 154040569, 460079341) and 
                created_at <= %(date_end)s::date and state not in ('init', 'start', 'confirm')
            group by state
            order by count(id) desc
            limit 7
            """
        with connection.cursor() as cursor:
            cursor.execute(query, {'date_end': date_end})
            data = cursor.fetchall()
            return data

    @classmethod
    def get_warehouse_monitoring(cls, date_start: date, date_end: date):
        query = """
        with date_series as (
            select generate_series(
                date_trunc('week', %(date_start)s::date),
                date_trunc('week', %(date_end)s::date),
                ('1 week')::interval
            ) :: date date
        ), wh_count as (
            select ds.date, count(id) request_count
            from date_series ds
            left join support_warehouserequest whr on date_trunc('week', whr.created_at)::date = ds.date
            group by ds.date
        ), wh_users as (
            select date, count(user_id) user_count
            from (
                select distinct ds.date, user_id
                from date_series ds
                left join support_warehouserequest whr on date_trunc('week', whr.created_at)::date = ds.date
            ) as t
            group by date
        ), wh_responses as (
            select ds.date, count(id) response_count
            from date_series ds
            left join support_warehouseresponse whr on date_trunc('week', whr.created_at)::date = ds.date
            group by date
        ), wh_files as (
            select ds.date, count(id) files_count
            from date_series ds
            left join support_warehouseresponse whr on date_trunc('week', whr.created_at)::date = ds.date
            where file is not null
            group by date
        )

        select
            (ds.date + interval '6 days')::date,
            coalesce(request_count, 0) request_count,
            coalesce(user_count, 0) user_count,
            coalesce(response_count, 0) response_count,
            coalesce(files_count, 0) files_count
        from date_series ds
        left join wh_count whc on ds.date = whc.date
        left join wh_users whu on ds.date = whu.date
        left join wh_responses whr on ds.date = whr.date
        left join wh_files whf on ds.date = whf.date
        order by date;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, {'date_start': date_start, 'date_end': date_end})
            data = dictfetchall(cursor)
            return data

    @classmethod
    def get_warehouse_total(cls, date_end: date):
        earliest_date = '2020-07-27'
        query = """
        with wh_count as (
            select count(*) request_count
            from support_warehouserequest
            where created_at > %(earliest_date)s::date and created_at < %(date_end)s::date
        ), wh_users as (
            select count(*) user_count
            from (
                select distinct user_id
                from support_warehouserequest
                where created_at > %(earliest_date)s::date and created_at < %(date_end)s::date
            ) t
        ), wh_responses as (
            select count(*) response_count
            from support_warehouseresponse
            where created_at > %(earliest_date)s::date and created_at < %(date_end)s::date
        ), wh_files as (
            select count(*) files_count
            from support_warehouseresponse
            where file is not null and created_at > %(earliest_date)s::date and created_at < %(date_end)s::date
        )

        select
            coalesce(request_count, 0) request_count,
            coalesce(user_count, 0) user_count,
            coalesce(response_count, 0) response_count,
            coalesce(files_count, 0) files_count
        from wh_count whc
        cross join wh_users whu
        cross join wh_responses wh
        cross join wh_files whf
        """
        with connection.cursor() as cursor:
            cursor.execute(query, {'earliest_date': earliest_date, 'date_end': date_end})
            data = dictfetchall(cursor)
            return data

    @classmethod
    def get_user_incidents(cls, user_id):
        now = get_now_msk()
        return Issue.objects.filter(
            Q(is_done=False) | Q(is_done=True, updated_at__gt=now - timedelta(days=1)),
            user_id=user_id
        ).order_by('-created_at').values('id', 'issue_id', 'is_done')
