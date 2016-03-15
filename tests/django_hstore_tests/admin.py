from pkg_resources import parse_version
from django.contrib import admin
from django import get_version
from .models import *  # noqa


class DataBagAdmin(admin.ModelAdmin):
    pass


class DefaultsInlineAdmin(admin.StackedInline):
    model = DefaultsInline
    extra = 0


class DefaultsModelAdmin(admin.ModelAdmin):
    inlines = [DefaultsInlineAdmin]


class RefsBagAdmin(admin.ModelAdmin):
    pass


admin.site.register(DataBag, DataBagAdmin)
admin.site.register(SerializedDataBag, DataBagAdmin)
admin.site.register(DefaultsModel, DefaultsModelAdmin)
admin.site.register(RefsBag, RefsBagAdmin)


if parse_version(get_version()) >= parse_version('1.6'):
    class SchemaDataBagAdmin(admin.ModelAdmin):
        list_display = ['name']

    admin.site.register(SchemaDataBag, SchemaDataBagAdmin)
