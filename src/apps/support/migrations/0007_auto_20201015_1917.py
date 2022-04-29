# Generated by Django 2.2.3 on 2020-10-15 19:17
import re

from django.db import migrations, models


def get_user_id_for_issue(apps, schema_editor):
    Issue = apps.get_model('support', 'Issue')
    BotUser = apps.get_model('bot_user', 'BotUser')
    issues = Issue.objects.all()
    for issue in issues:
        result = re.findall(r'\((\d*)\)', issue.title)
        phone = result[0] if result else None
        user_id = 120106597
        if phone:
            user = BotUser.objects.filter(phone=phone).first()
            user_id = user.tg_id if user else user_id
        issue.user_id = user_id
        issue.save()


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('support', '0006_issue'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='is_done',
            field=models.BooleanField(default=False, verbose_name='Завершена ли задача?'),
        ),
        migrations.AddField(
            model_name='issue',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения'),
        ),
        migrations.AddField(
            model_name='issue',
            name='user_id',
            field=models.IntegerField(null=True, blank=True, verbose_name='ID клиента, создавшего инцидент'),
        ),
        migrations.RunPython(get_user_id_for_issue, reverse_func),
        migrations.AlterField(
            model_name='issue',
            name='user_id',
            field=models.IntegerField(default=120106597, verbose_name='ID клиента, создавшего инцидент'),
            preserve_default=False,
        ),

    ]