from django.forms import Field
from django.utils import simplejson as json
from django.contrib.admin.widgets import AdminTextareaWidget

from django_hstore import util

class JsonMixin(object):

    def to_python(self, value):
        return json.loads(value)

    def render(self, name, value, attrs=None):
        value = json.dumps(value, sort_keys=True, indent=2)
        return super(JsonMixin, self).render(name, value, attrs)


class DictionaryFieldWidget(JsonMixin, AdminTextareaWidget):
    pass


class ReferencesFieldWidget(JsonMixin, AdminTextareaWidget):

    def render(self, name, value, attrs=None):
        value = util.serialize_references(value)
        return super(ReferencesFieldWidget, self).render(name, value, attrs)


class DictionaryField(JsonMixin, Field):
    """
    A dictionary form field.
    """
    def __init__(self, **params):
        params['widget'] = DictionaryFieldWidget
        super(DictionaryField, self).__init__(**params)


class ReferencesField(JsonMixin, Field):
    """
    A references form field.
    """
    def __init__(self, **params):
        params['widget'] = ReferencesFieldWidget
        super(ReferencesField, self).__init__(**params)

    def to_python(self, value):
        value = super(ReferencesField, self).to_python(value)
        return util.unserialize_references(value)
