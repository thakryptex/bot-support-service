from dataclasses import dataclass

from atlas_utils.common.base_dto import Dto


@dataclass
class AuthMetaDto(Dto):
    token: str
    is_new_user: bool


@dataclass
class AuthDataDto(Dto):
    type: str
    id: str
    attributes: dict


@dataclass
class AuthDto(Dto):
    meta: AuthMetaDto
    data: AuthDataDto
