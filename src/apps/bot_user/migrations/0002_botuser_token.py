# Generated by Django 2.2.3 on 2020-01-19 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='token',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Последний токен'),
        ),
    ]
