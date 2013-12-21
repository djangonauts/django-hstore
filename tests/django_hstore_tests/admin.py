from django.contrib import admin
from .models import *


class DataBagAdmin(admin.ModelAdmin):
    pass


class DefaultsModelAdmin(admin.ModelAdmin):
    pass


class RefsBagAdmin(admin.ModelAdmin):
    pass


admin.site.register(DataBag, DataBagAdmin)
admin.site.register(DefaultsModel, DefaultsModelAdmin)
admin.site.register(RefsBag, RefsBagAdmin)