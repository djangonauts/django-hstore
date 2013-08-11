try:
    import simplejson as json
except ImportError:
    import json

from django.forms import Field
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from django_hstore import util


def validate_hstore(string):
    """ HSTORE validation """
    # if empty
    if string == '' or string == 'null':
        string = '{}'
    
    # ensure valid JSON
    try:
        dictionary = json.loads(string)
    except json.scanner.JSONDecodeError as e:
        raise ValidationError(_('Invalid JSON: %s') % e.message)
    
    # ensure is a dictionary
    if not isinstance(dictionary, dict):
        raise ValidationError(_('No lists or strings allowed, only dictionaries'))
    
    # convert any non string object into string
    for key, value in dictionary.iteritems():
        if isinstance(value, dict) or isinstance(value, list):
            dictionary[key] = json.dumps(value)
        elif isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
            dictionary[key] = unicode(value).lower()
    
    return dictionary


class JsonMixin(object):
    def to_python(self, value):
        return validate_hstore(value)

    def render(self, name, value, attrs=None):
        # return json representation of a meaningful value
        # doesn't show anything for None, empty strings or empty dictionaries
        if value and not isinstance(value, basestring):
            value = json.dumps(value, sort_keys=True, indent=4)
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
