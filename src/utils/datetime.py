from datetime import timedelta

import pytz
from django.utils import timezone

iso_format = '%Y-%m-%d'
month_format = '%Y-%m'
date_format_range = '%d.%m.%Y'


def get_now_msk():
    return timezone.now().astimezone(pytz.timezone('Europe/Moscow'))


def get_now_date_msk():
    return get_now_msk().date()


def get_week_start_and_end_dates(date_obj):
    start_of_week = date_obj - timedelta(days=date_obj.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_four_weeks_from_date(date_obj):
    date_start = date_obj - timedelta(days=date_obj.weekday()) - timedelta(days=21)
    date_end = date_obj + timedelta(days=6 - date_obj.weekday())
    return date_start, date_end
