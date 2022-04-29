from django.db import migrations, models


def assignee_id(apps, schema_editor):
    Assignee = apps.get_model('bot_user', 'Assignee')

    Assignee.objects.filter(username='mkulagina').update(jira_id='6009a051ea0e64006b7560b6')
    Assignee.objects.filter(username='nlybimova').update(jira_id='60099fcfe2a13500697dcd17')
    Assignee.objects.filter(username='daegorov').update(jira_id='600991c7e64c95006fe27177')


def revert_assignee_id(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bot_user', '0006_auto_20210511_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignee',
            name='jira_id',
            field=models.CharField(default='1234', max_length=32, verbose_name='ID в Jira'),
            preserve_default=False,
        ),

        migrations.RunPython(assignee_id, revert_assignee_id)
    ]
