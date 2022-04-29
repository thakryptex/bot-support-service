__all__ = ('JIRA_CLIENT_KWARGS',)

from envparse import env

JIRA_CLIENT_KWARGS = {
    'base_url': env('JIRA_URL', default='https://it-labs.atlassian.net/rest/api/2/'),
    'timeout': (env.float('JIRA_CONNECT_TIMEOUT_SEC', default=1.0),
                env.float('JIRA_READ_TIMEOUT_SEC', default=5.0)),
}
