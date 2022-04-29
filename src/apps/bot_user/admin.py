from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from apps.bot_user.forms import MenuNodeForm
from apps.bot_user.models import FAQ, MenuNode, Assignee


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'order_weight']
    search_fields = ['question', 'answer']


@admin.register(Assignee)
class AssigneeAdmin(admin.ModelAdmin):
    list_display = ['username', 'name']


@admin.register(MenuNode)
class MenuNodeAdmin(DraggableMPTTAdmin):
    form = MenuNodeForm
    mptt_level_indent = 20
    fields = ['parent', 'parents', 'input_waiting', 'button_name', 'title', 'description', 'ordering', 'node_id',
              'issue_type', 'assignee']
    inlines = []
