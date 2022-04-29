import logging
from io import BytesIO

import ujson
from django.conf import settings
from requests.auth import HTTPBasicAuth

from services.client import BaseClient
from services.jira.dto import JiraIssue
from services.jira.settings import JIRA_CLIENT_KWARGS

logger = logging.getLogger(__name__)

__all__ = ('client', 'JiraClient',)


class JiraClient(BaseClient):
    def create_issue(self, issue: JiraIssue):
        try:
            response = self._post('issue/', data=ujson.dumps({'fields': issue.to_dict()}),
                                  headers={'content-type': 'application/json'},
                                  auth=HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_TOKEN))
            return response.get('key')
        except Exception as e:
            logger.error(e)
            raise e

    def get_issue_status(self, issue_id):
        try:
            response = self._get(f'issue/{issue_id}',
                                 auth=HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_TOKEN))
            status_key = response['fields']['status']['statusCategory']['key']
            return status_key  # == 'done'
        except Exception as e:
            logger.error(e)

    def upload_attachment(self, task_id, file):
        self._post(f'issue/{task_id}/attachments', headers={'X-Atlassian-Token': 'nocheck'},
                   files={'file': BytesIO(file)}, auth=HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_TOKEN))


jira_client = JiraClient(**JIRA_CLIENT_KWARGS)
