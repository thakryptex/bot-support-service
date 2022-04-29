from django.conf import settings

from services.jira.dto import JiraIssue


class JiraIssueFactory:

    @classmethod
    def dto_from_dict(cls, data) -> JiraIssue:
        title = ' '.join(data['title'].split())
        if len(title) >= 255:
            title = title[:250] + '...'
        return JiraIssue(
            project={'key': settings.JIRA_PROJECT_KEY},
            description=data['description'],
            issuetype={'id': data['issue_type']},
            assignee={'id': data['assignee']},
            summary=title,
        )
