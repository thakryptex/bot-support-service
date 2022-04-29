from dataclasses import dataclass

from atlas_utils.common.base_dto import Dto


@dataclass
class JiraIssue(Dto):
    project: dict
    summary: str
    description: str
    issuetype: dict
    assignee: dict = None
    labels: list = None
