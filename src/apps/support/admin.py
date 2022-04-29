from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from apps.support.models import SupportRequest, Message, WarehouseRequest, WarehouseResponse, Issue


class HasMimFilter(SimpleListFilter):
    title = 'МИМ назначен'
    parameter_name = 'has_mim'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Назначен'),
            ('false', 'Не назначен'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(mim__isnull=False)
        elif self.value() == 'false':
            return queryset.filter(mim__isnull=True)
        else:
            return queryset


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['request', 'is_auto', 'from_user', 'text', 'file']
    readonly_fields = ['created_at']


def file_link(obj):
    if obj.file:
        return format_html('<a href="{0}" target="_blank">{1}</a>', obj.file.url, obj.file)
    return ''
file_link.allow_tags = True
file_link.short_description = 'Ссылка'


class WarehouseResponseInline(admin.TabularInline):
    model = WarehouseResponse
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    fields = ['text', file_link, 'created_at']
    readonly_fields = [file_link, 'created_at']


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ['bot_user_id', 'mim', 'theme', 'is_done']
    list_filter = ['is_done', HasMimFilter]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['request', 'created_at', 'is_auto', 'from_user', 'text']


@admin.register(WarehouseRequest)
class WarehouseRequestAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'user_id', 'request', 'created_at']
    search_fields = ['request', 'user_id', 'responses__text']
    inlines = [WarehouseResponseInline]

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'title', 'description', 'created_at', 'issue_id', 'is_done']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['is_done']
    search_fields = ['user_id', 'issue_id', 'title', 'description']
