# Generated by Django 2.2.3 on 2020-01-10 15:10

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('tg_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID в Телеграме')),
                ('name', models.CharField(max_length=128, verbose_name='Имя')),
                ('username', models.CharField(blank=True, max_length=32, null=True, verbose_name='Ник в телеграме')),
                ('phone', models.CharField(blank=True, max_length=13, null=True, verbose_name='Телефон')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время первого сообщения к боту')),
                ('last_message', models.IntegerField(default=1, verbose_name='ID последнего сообщения')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Хранилище')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='storage', to='bot_user.BotUser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Хранилище',
                'verbose_name_plural': 'Хранилища',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=32, verbose_name='Состояние')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время переключения состояния')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='bot_user.BotUser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Состояние',
                'verbose_name_plural': 'Состояния',
                'ordering': ['user', '-created_at'],
            },
        ),
    ]
