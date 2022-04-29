from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.db.models.functions import Coalesce

from apps.bot_user.constants import IssueType
from apps.bot_user.models import MenuNode


def get_next_ordering_number(parent):
    return MenuNode.objects.filter(parent=parent).aggregate(
        ordering_max=Coalesce(Max('ordering') + 1, 100))['ordering_max']


class MenuNodeForm(forms.ModelForm):
    class Meta:
        model = MenuNode
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_waiting'].help_text = 'В одном меню разрешён либо ввод текста, либо наличие кнопок. ' \
                                                 'Объединить их сейчас нельзя.'
        self.fields['title'].help_text = 'Текст, показываемый пользователю бота, в оглавлении меню. ' \
                                         'Вопрос или описание дальнейших действий для пользователя.'

        self.fields['button_name'].required = False
        self.fields['button_name'].help_text = 'Текст, показываемый пользователю бота, на кнопке в меню'

        self.fields['node_id'].required = False
        self.fields['node_id'].help_text = 'Идентификатор звена в цепочке переходов по меню'
        self.fields['node_id'].widget = forms.TextInput(attrs={'readonly': True})

        self.fields['ordering'].required = False
        self.fields['ordering'].help_text = 'Порядок (чем меньше число, тем выше в списке)'

        self.fields['issue_type'].help_text = 'Назначается для всей последующей цепочки меню'
        self.fields['assignee'].help_text = 'Кто ответственный за данную ветку инцидентов ' \
                                            '(вся последующая ветка назначается на этого человека)'

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data['parent']
        ordering = cleaned_data['ordering']
        if ordering is None:
            cleaned_data['ordering'] = get_next_ordering_number(parent)
        return cleaned_data
