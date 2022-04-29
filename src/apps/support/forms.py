from datetime import datetime

from atlas_utils.common.exceptions import ValidationError
from django import forms

from utils.datetime import get_now_date_msk, date_format_range, get_four_weeks_from_date


class RangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def __init__(self, *args, default_start=None, default_end=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_start = default_start
        self.default_end = default_end

    def clean_daterange(self):
        daterange = self.cleaned_data['daterange']
        if daterange:
            daterange = daterange.split('-')
            if len(daterange) != 2:
                raise ValidationError('Диапазон указан неверно, должно быть две даты через "-".')
            try:
                for index, date_str in enumerate(daterange):
                    daterange[index] = datetime.strptime(date_str.strip(), date_format_range).date()
            except Exception:
                raise ValidationError('Некорректный формат даты.')
            return daterange
        else:
            if self.default_start and self.default_end:
                return self.default_start, self.default_end
            else:
                today = get_now_date_msk()
                return get_four_weeks_from_date(today)

