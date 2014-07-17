from django.contrib import admin
from django import forms


class HStoreSchemaForm(forms.ModelForm):
    def full_clean(self):
        self.instance._add_hstore_virtual_fields_to_fields()
        super(HStoreSchemaForm, self).full_clean()
        self.instance._remove_hstore_virtual_fields_from_fields()


class HStoreSchemaAdmin(admin.ModelAdmin):
    form = HStoreSchemaForm
    