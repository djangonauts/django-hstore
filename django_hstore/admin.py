from django.contrib import admin
from django import forms


class HStoreSchemaForm(forms.ModelForm):
    def full_clean(self):
        """
        perform validation also on hstore virtual fields
        """
        self.instance._add_hstore_virtual_fields_to_fields()
        try:
            super(HStoreSchemaForm, self).full_clean()
        except Exception as e:
            raise e
        # ensure virtual fields are removed
        finally:
            self.instance._remove_hstore_virtual_fields_from_fields()

class HStoreSchemaAdmin(admin.ModelAdmin):
    form = HStoreSchemaForm
    