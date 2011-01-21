try:
    import yaml
    def _to_python(value):
        return yaml.load(value)
    def _to_text(value):
        return yaml.dump(value, default_flow_style=False)
except ImportError:
    import json
    def _to_python(value):
        return json.loads(value)
    def _to_text(value):
        return json.dumps(value, sort_keys=True, indent=2)

from django.contrib.admin.widgets import AdminTextareaWidget
from django.forms import Field

from django_hstore import util

class DictionaryFieldWidget(AdminTextareaWidget):
    def render(self, name, value, attrs=None):
        return super(DictionaryFieldWidget, self).render(name, _to_text(value), attrs)

class DictionaryField(Field):
    """A dictionary form field."""

    def __init__(self, **params):
        params['widget'] = DictionaryFieldWidget
        super(DictionaryField, self).__init__(**params)

    def to_python(self, value):
        return _to_python(value)

class ReferencesFieldWidget(AdminTextareaWidget):
    def render(self, name, value, attrs=None):
        value = util.serialize_references(value)
        return super(ReferencesFieldWidget, self).render(name, _to_text(value), attrs)

class ReferencesField(Field):
    """A references form field."""

    def __init__(self, **params):
        params['widget'] = ReferencesFieldWidget
        super(ReferencesField, self).__init__(**params)

    def to_python(self, value):
        return util.unserialize_references(_to_python(value))
