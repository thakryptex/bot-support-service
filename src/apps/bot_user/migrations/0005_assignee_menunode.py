import django.db.models.deletion
import mptt.fields
from django.db import connection, transaction, migrations, models


def create_nodes(apps, schema_editor):
    Assignee = apps.get_model('bot_user', 'Assignee')
    MenuNode = apps.get_model('bot_user', 'MenuNode')

    Assignee.objects.bulk_create([
        Assignee(username='daegorov', name='Егоров Дмитрий'),
        Assignee(username='mkulagina', name='Кулагина Мария'),
        Assignee(username='sdolgushina', name='Попова Светлана'),
    ])

    MenuNode.objects.bulk_create([
        MenuNode(id=10, node_id="node_vel_sebya_jg4OTQ4", ordering=2, button_name="Вёл себя некорректно", title="Введите номер заказа", description=None, lft=23, rght=24, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=31, node_id="node_ne_vernyi_TI4NDYw", ordering=5, button_name="Не верный размер", title="Введите номер заказа", description=None, lft=49, rght=50, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=20, node_id="node_ne_predost_TA0MDY1", ordering=4, button_name="Не предоставил терминал/терминал не работал", title="Введите номер заказа", description=None, lft=27, rght=28, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=21, node_id="node_ne_imel_sd_TE4NDc3", ordering=5, button_name="Не имел сдачи", title="Введите номер заказа", description=None, lft=29, rght=30, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=22, node_id="node_neverno_pr_zAzNDgy", ordering=6, button_name="Неверно пробил сумму выкупа", title="Введите номер заказа", description=None, lft=31, rght=32, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=23, node_id="node_otkazal_v_zA0NjI0", ordering=7, button_name="Отказал в  частичном выкупе", title="Введите номер заказа", description=None, lft=33, rght=34, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=11, node_id="node_vvod_Tc0NTkx", ordering=100, button_name="Ввод текста", title="Расскажите подробнее об инциденте", description=None, lft=18, rght=21, tree_id=3, level=3, input_waiting=True, parent_id=9, issue_type=None, assignee_id=None),
        MenuNode(id=33, node_id="node_cena_na_up_Dg1NDUz", ordering=7, button_name="Цена на упаковке отличается от цены в заказе", title="Введите номер заказа", description=None, lft=53, rght=54, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=16, node_id="node_s_zakazom_TU1MDcx", ordering=3, button_name="С заказом", title="С какой проблемой вы столкнулись?", description=None, lft=36, rght=57, tree_id=3, level=1, input_waiting=False, parent_id=15, issue_type="10005", assignee_id="mkulagina"),
        MenuNode(id=25, node_id="node_tovar_s_de_DE4MTM3", ordering=1, button_name="Товар с дефектом", title="Введите номер заказа", description=None, lft=37, rght=42, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=27, node_id="node_vvod_DAwNTQz", ordering=100, button_name="Ввод текста", title="Спасибо за Ваше обращение!", description=None, lft=39, rght=40, tree_id=3, level=4, input_waiting=True, parent_id=26, issue_type=None, assignee_id=None),
        MenuNode(id=15, node_id="incident", ordering=3, button_name="Инцидент", title="С чем возникла проблема?", description=None, lft=1, rght=72, tree_id=3, level=0, input_waiting=False, parent_id=None, issue_type=None, assignee_id=None),
        MenuNode(id=24, node_id="node_oshibka_na_TkwNTUx", ordering=4, button_name="Ошибка на сайте/в приложении", title="С какой проблемой вы столкнулись?", description=None, lft=58, rght=71, tree_id=3, level=1, input_waiting=False, parent_id=15, issue_type="10008", assignee_id="sdolgushina"),
        MenuNode(id=18, node_id="node_ne_predost_jM0OTcw", ordering=4, button_name="Не предоставил достоверную информацию", title="Введите имя оператора", description=None, lft=13, rght=14, tree_id=3, level=2, input_waiting=False, parent_id=2, issue_type=None, assignee_id=None),
        MenuNode(id=2, node_id="node_s_operatorom", ordering=1, button_name="С оператором", title="В чём ошибся оператор?", description=None, lft=2, rght=15, tree_id=3, level=1, input_waiting=False, parent_id=15, issue_type="10005", assignee_id="sdolgushina"),
        MenuNode(id=29, node_id="node_istek_srok_zQxNTU5", ordering=3, button_name="Истёк срок годности", title="Введите номер заказа", description=None, lft=45, rght=46, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=12, node_id="node_vvod_TYzNTMz", ordering=100, button_name="Ввод текста", title="Спасибо за Ваше обращение!", description=None, lft=19, rght=20, tree_id=3, level=4, input_waiting=True, parent_id=11, issue_type=None, assignee_id=None),
        MenuNode(id=35, node_id="node_nekorrektn_jA5MTMy", ordering=1, button_name="Некорректная цена или скидка", title="Введите артикулы товаров с некорректной ценой или скидкой", description=None, lft=59, rght=64, tree_id=3, level=2, input_waiting=False, parent_id=24, issue_type=None, assignee_id=None),
        MenuNode(id=19, node_id="node_byl_bez_ma_DYzOTg3", ordering=3, button_name="Был без маски и/или перчаток", title="Введите номер заказа", description=None, lft=25, rght=26, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=9, node_id="node_priehal_ne_TI3NzQy", ordering=1, button_name="Приехал невовремя", title="Введите номер заказа", description=None, lft=17, rght=22, tree_id=3, level=2, input_waiting=False, parent_id=3, issue_type=None, assignee_id=None),
        MenuNode(id=37, node_id="node_oshibka_v_DA2NTM5", ordering=3, button_name="Ошибка в карточке товара", title="Введите артикулы товаров с некорректной информацией", description=None, lft=67, rght=68, tree_id=3, level=2, input_waiting=False, parent_id=24, issue_type=None, assignee_id=None),
        MenuNode(id=39, node_id="node_vvod_Tk5Mzk4", ordering=100, button_name="Ввод текста", title="Расскажите подробнее об инциденте", description=None, lft=60, rght=63, tree_id=3, level=3, input_waiting=True, parent_id=35, issue_type=None, assignee_id=None),
        MenuNode(id=28, node_id="node_povrejdena_DUyMzE2", ordering=2, button_name="Повреждена упаковка", title="Введите номер заказа", description=None, lft=43, rght=44, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=30, node_id="node_ne_tot_tov_Tc5NDU3", ordering=4, button_name="Не тот товар в заказе", title="Введите номер заказа", description=None, lft=47, rght=48, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=32, node_id="node_ne_dolojil_jk3NDU5", ordering=6, button_name="Не доложили товар в заказ", title="Введите номер заказа", description=None, lft=51, rght=52, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=34, node_id="node_otsutstvov_zIwNTEz", ordering=8, button_name="Отсутствовал товар после оформления заказа", title="Введите номер заказа", description=None, lft=55, rght=56, tree_id=3, level=2, input_waiting=False, parent_id=16, issue_type=None, assignee_id=None),
        MenuNode(id=26, node_id="node_vvod_TQ2OTIx", ordering=100, button_name="Ввод текста", title="Расскажите подробнее об инциденте", description=None, lft=38, rght=41, tree_id=3, level=3, input_waiting=True, parent_id=25, issue_type=None, assignee_id=None),
        MenuNode(id=36, node_id="node_problemy_s_Tk1MTE1", ordering=2, button_name="Проблемы с таблицей размеров", title="Расскажите подробнее об инциденте", description=None, lft=65, rght=66, tree_id=3, level=2, input_waiting=False, parent_id=24, issue_type=None, assignee_id=None),
        MenuNode(id=38, node_id="node_tehnichesk_zg5NDQ3", ordering=4, button_name="Техническая ошибка", title="Расскажите подробнее об инциденте", description=None, lft=69, rght=70, tree_id=3, level=2, input_waiting=False, parent_id=24, issue_type=None, assignee_id=None),
        MenuNode(id=40, node_id="node_vvod_Tc4ODI0", ordering=100, button_name="Ввод текста", title="Спасибо за Ваше обращение!", description=None, lft=61, rght=62, tree_id=3, level=4, input_waiting=True, parent_id=39, issue_type=None, assignee_id=None),
        MenuNode(id=7, node_id="node_vvod_jYwNjk0", ordering=1, button_name="Ввод текста", title="Расскажите подробнее об инциденте", description=None, lft=4, rght=7, tree_id=3, level=3, input_waiting=True, parent_id=17, issue_type=None, assignee_id=None),
        MenuNode(id=8, node_id="node_vvod_DUzMzMy", ordering=100, button_name="Ввод текста", title="Спасибо за Ваше обращение!", description=None, lft=5, rght=6, tree_id=3, level=4, input_waiting=True, parent_id=7, issue_type=None, assignee_id=None),
        MenuNode(id=4, node_id="node_ne_perezvo_TE3MTQ1", ordering=1, button_name="Не перезвонил", title="Введите имя оператора", description=None, lft=9, rght=10, tree_id=3, level=2, input_waiting=False, parent_id=2, issue_type=None, assignee_id=None),
        MenuNode(id=5, node_id="node_byl_grub_zM2MDU1", ordering=2, button_name="Был груб", title="Введите имя оператора", description=None, lft=11, rght=12, tree_id=3, level=2, input_waiting=False, parent_id=2, issue_type=None, assignee_id=None),
        MenuNode(id=17, node_id="node_ne_vnes_ko_TQ1Mzkx", ordering=1, button_name="Не внёс корректировки в заказ", title="Введите имя оператора", description=None, lft=3, rght=8, tree_id=3, level=2, input_waiting=False, parent_id=2, issue_type=None, assignee_id=None),
        MenuNode(id=3, node_id="node_s_kurerom_zc4NTEw", ordering=2, button_name="С курьером", title="В чём ошибся курьер?", description=None, lft=16, rght=35, tree_id=3, level=1, input_waiting=False, parent_id=15, issue_type="10005", assignee_id="daegorov")
    ])

    # проставление связей для m2m
    cursor = connection.cursor()
    query = "INSERT INTO public.bot_user_menunode_parents (id, from_menunode_id, to_menunode_id) VALUES (%s,%s,%s)"
    variables = [
        (1, 7, 4), (2, 7, 5), (3, 4, 7), (4, 5, 7), (5, 11, 9), (6, 11, 10), (7, 9, 11), (8, 10, 11), (9, 7, 17),
        (10, 7, 18), (11, 11, 19), (12, 11, 20), (13, 11, 21), (14, 11, 22), (15, 11, 23), (16, 24, 15), (17, 26, 25),
        (18, 27, 26), (19, 26, 32), (20, 26, 33), (21, 26, 34), (22, 26, 28), (23, 26, 29), (24, 26, 30), (25, 26, 31),
        (26, 39, 35), (28, 39, 37), (29, 39, 38), (30, 40, 39), (31, 40, 36)
    ]
    cursor.executemany(query, variables)


def delete_nodes(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bot_user', '0004_faq'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignee',
            fields=[
                ('username', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='Юзернейм в jira')),
                ('name', models.CharField(max_length=64, verbose_name='Имя пользователя')),
            ],
            options={
                'verbose_name': 'Исполнитель',
                'verbose_name_plural': 'Исполнители',
            },
        ),
        migrations.CreateModel(
            name='MenuNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.CharField(max_length=32, unique=True, verbose_name='ID ноды')),
                ('ordering', models.PositiveIntegerField(verbose_name='Порядок в списке')),
                ('input_waiting', models.BooleanField(default=False, verbose_name='Ожидает ввод текста пользователем?')),
                ('button_name', models.CharField(max_length=50, verbose_name='Текст кнопки')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Описание')),
                ('issue_type', models.CharField(blank=True, choices=[('10005', 'История'), ('10008', 'Ошибка')], max_length=6, null=True, verbose_name='Какой тип задачи заводить')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot_user.Assignee', verbose_name='На кого назначать задачу на доске')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='bot_user.MenuNode', verbose_name='Предыдущее меню')),
                ('parents', mptt.fields.TreeManyToManyField(blank=True, related_name='children_m2m', to='bot_user.MenuNode', verbose_name='Предыдущие меню')),
            ],
            options={
                'verbose_name': 'Цепочка переходов по меню',
                'verbose_name_plural': 'Цепочки переходов в меню',
            },
        ),

        migrations.RunPython(create_nodes, delete_nodes)

    ]
