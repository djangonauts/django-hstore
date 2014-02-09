from django.contrib import admin
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