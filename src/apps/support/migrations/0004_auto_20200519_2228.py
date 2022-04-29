# Generated by Django 2.2.3 on 2020-05-19 22:28

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0003_auto_20200227_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='sent_to_blinger',
        ),
        migrations.AlterField(
            model_name='message',
            name='file',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='Прикреплённый файл'),
        ),
    ]