import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from apps.support.forms import RangeForm
from apps.support.service import SupportService
from utils.datetime import get_now_date_msk, get_four_weeks_from_date, date_format_range
from utils.decorators import error_processing


@method_decorator(error_processing('2.0'), name='dispatch')
class MonitorView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('admin:login')
    redirect_field_name = 'next'
    template_name = 'monitor.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        today = get_now_date_msk()
        date_start, date_end = get_four_weeks_from_date(today)
        form = RangeForm(self.request.GET)
        if form.is_valid():
            date_start, date_end = form.cleaned_data['daterange']
        monitor = SupportService.get_bot_monitor(date_end)
        metrics, date_headers = SupportService.get_warehouse_monitoring(date_start, date_end)
        context['monitor'] = monitor
        context['date_headers'] = date_headers
        context['metrics'] = metrics
        context['daterange'] = f'{date_start.strftime(date_format_range)} - ' \
                               f'{date_end.strftime(date_format_range)}'
        return context


@method_decorator(error_processing('2.0'), name='dispatch')
class BlingerWebhookView(View):

    def post(self, request, *args, **kwargs):
        params = json.loads(request.body)
        channel_id = params['custom_channel_id']
        if channel_id == settings.BLINGER_CHANNEL_ID:
            SupportService.handle_blinger_webhook(params)
        return HttpResponse()

