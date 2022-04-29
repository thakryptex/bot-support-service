from celery import shared_task

from apps.support.service import SupportService
from logger import app_logger


@shared_task(bind=True, name='refresh_issue_statuses')
def refresh_issue_statuses(task):
    try:
        issues = SupportService.get_unfinished_issues()
        for issue_id in issues:
            SupportService.update_issue_status(issue_id)
    except Exception as e:
        app_logger.exception(e)
