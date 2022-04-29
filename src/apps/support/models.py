from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class SupportRequest(models.Model):
    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'

    bot_user_id = models.CharField(max_length=64, verbose_name='ID пользователя в ТГ')
    theme = models.CharField(max_length=16, verbose_name='Контекст обращения')
    mim = models.ForeignKey(User, null=True, blank=True, related_name='support_requests',
                            verbose_name='Ответственный МИМ', on_delete=models.SET_NULL)
    is_done = models.BooleanField(default=False, verbose_name='Обработана ли заявка?')

    def __str__(self):
        return f'Заявка {self.id} от {self.bot_user_id}, тема {self.theme}'


class Message(models.Model):
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    request = models.ForeignKey(SupportRequest, related_name='messages',
                                verbose_name='Запрос', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    is_auto = models.BooleanField(default=True, verbose_name='Автоматический ответ')
    from_user = models.BooleanField(default=True, verbose_name='Сообщение от пользователя?')
    text = models.TextField(null=True, blank=True, verbose_name='Текст обращения')
    file = CloudinaryField(folder='herb_bot', resource_type='image',
                           null=True, blank=True, verbose_name='Прикреплённый файл')

    def __str__(self):
        return f'Сообщение от {"пользователя" if self.from_user else "техподдержки"}: {self.text}.'


class WarehouseRequest(models.Model):
    class Meta:
        verbose_name = 'Запрос к складу'
        verbose_name_plural = 'Запросы к складу'
        ordering = ['created_at']

    message_id = models.IntegerField(verbose_name='ID сообщения')
    user_id = models.IntegerField(verbose_name='ID клиента, запросившего фото')
    request = models.TextField(verbose_name='Запрос клиента')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    def __str__(self):
        return f'Запрос к складу {self.id}.'


class WarehouseResponse(models.Model):
    class Meta:
        verbose_name = 'Ответ склада'
        verbose_name_plural = 'Ответы склада'
        ordering = ['created_at']

    request = models.ForeignKey(
        WarehouseRequest, related_name='responses', verbose_name='Запрос', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True, verbose_name='Текст обращения')
    file = CloudinaryField(folder='herb_bot', resource_type='image',
                           null=True, blank=True, verbose_name='Прикреплённый файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    def __str__(self):
        return f'Ответ склада {self.id}.'


class Issue(models.Model):
    class Meta:
        verbose_name = 'Инцидент'
        verbose_name_plural = 'Инциденты'

    user_id = models.IntegerField(verbose_name='ID клиента, создавшего инцидент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')
    title = models.TextField(verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    issue_id = models.CharField(max_length=16, verbose_name='ID задачи')
    is_done = models.BooleanField(default=False, verbose_name='Завершена ли задача?')

    def __str__(self):
        return f'Инцидент {self.issue_id}: {self.title}.'


@receiver(post_save, sender=Message)
def notify_new_message_receiver(sender, instance, created, **kwargs):
    # отправлять уведомление лишь со второго сообщения
    if created and instance.request.messages.count() > 1:
        if not instance.from_user:
            from apps.bot_user.handlers import notify_user
            notify_user(instance)
