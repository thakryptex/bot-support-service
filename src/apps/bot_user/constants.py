warehouse_text = 'запросил фотографии товара'


def full_warehouse_text(client_id):
    return f'{client_id or "Клиент"} {warehouse_text}'


class IssueType:
    STORY = '10005'
    ERROR = '10008'

    @classmethod
    def choices(cls):
        return (
            (cls.STORY, 'История'),
            (cls.ERROR, 'Ошибка'),
        )
