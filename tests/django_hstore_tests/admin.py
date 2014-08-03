from django.contrib import admin
from django import get_version
from .models import *


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
admin.site.register(DefaultsModel, DefaultsModelAdmin)
admin.site.register(RefsBag, RefsBagAdmin)


if get_version()[0:3] >= '1.6':
    class SchemaDataBagAdmin(admin.ModelAdmin):
        list_display = ['name']
    
    admin.site.register(SchemaDataBag, SchemaDataBagAdmin)
