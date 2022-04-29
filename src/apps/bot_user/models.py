from django.contrib.postgres.fields import JSONField
from django.db import models
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel

from apps.bot_user.constants import IssueType
from utils.bot import AbstractStateModel


class BotUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    tg_id = models.IntegerField(primary_key=True, verbose_name='ID в Телеграме')
    name = models.CharField(max_length=128, verbose_name='Имя')
    username = models.CharField(max_length=32, null=True, blank=True, verbose_name='Ник в телеграме')
    phone = models.CharField(max_length=13, null=True, blank=True, verbose_name='Телефон')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время первого сообщения к боту')
    last_message = models.IntegerField(default=1, verbose_name='ID последнего сообщения')
    token = models.CharField(max_length=512, null=True, blank=True, verbose_name='Последний токен')

    herb_id = models.IntegerField(null=True, blank=True, verbose_name='ID в Pyramid')


class State(AbstractStateModel):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='states', verbose_name='Пользователь')


class Storage(models.Model):
    class Meta:
        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилища'

    user = models.OneToOneField(BotUser, on_delete=models.CASCADE, related_name='storage', verbose_name='Пользователь')
    data = JSONField(default=dict, verbose_name='Хранилище')


class FAQ(models.Model):
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['order_weight', 'question']

    order_weight = models.IntegerField(default=1, verbose_name='Сортировка (чем меньше, тем выше)')
    question = models.CharField(max_length=64, verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')


class Assignee(models.Model):
    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

    username = models.CharField(primary_key=True, max_length=32, verbose_name='Юзернейм в jira')
    name = models.CharField(max_length=64, verbose_name='Имя пользователя')
    jira_id = models.CharField(max_length=32, verbose_name='ID в Jira')

    def __str__(self):
        return self.name


class MenuNode(MPTTModel):
    class Meta:
        verbose_name = 'Цепочка переходов по меню'
        verbose_name_plural = 'Цепочки переходов в меню'

    class MPTTMeta:
        order_insertion_by = ['ordering', 'button_name']

    # TODO: check alternatives later:
    """
    https://github.com/funkybob/django-closure-tree
    https://github.com/elpaso/django-dag
    """

    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
                            verbose_name='Предыдущее меню')
    parents = TreeManyToManyField('self', symmetrical=False, blank=True, related_name='children_m2m',
                                  verbose_name='Предыдущие меню')

    node_id = models.CharField(max_length=32, unique=True, verbose_name='ID ноды')
    ordering = models.PositiveIntegerField(verbose_name='Порядок в списке')
    input_waiting = models.BooleanField(default=False, verbose_name='Ожидает ввод текста пользователем?')
    button_name = models.CharField(max_length=50, verbose_name='Текст кнопки')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Описание')

    issue_type = models.CharField(max_length=6, choices=IssueType.choices(), null=True, blank=True,
                                  verbose_name='Какой тип задачи заводить')
    assignee = models.ForeignKey(Assignee, null=True, blank=True, verbose_name='На кого назначать задачу на доске',
                                 on_delete=models.SET_NULL)

    def __str__(self):
        button_name = '' if self.input_waiting else '"{}" '.format(self.button_name)
        title = '{}{}'.format(self.title[:32], '...' if len(self.title) else '')
        return f'{button_name} -> {title}' if button_name else title
