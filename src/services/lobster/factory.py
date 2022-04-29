from services.lobster.dto import AuthDto, AuthMetaDto, AuthDataDto


class AuthDtoFactory:
    @classmethod
    def dto_from_dict(cls, item_dict):
        meta = AuthMetaDto(
            token=item_dict['meta']['token'],
            is_new_user=item_dict['meta']['isNewUser'],
        )
        data = AuthDataDto(
            type=item_dict['data']['type'],
            id=item_dict['data']['id'],
            attributes=item_dict['data']['attributes'],
        )
        return AuthDto(
            meta=meta,
            data=data
        )
