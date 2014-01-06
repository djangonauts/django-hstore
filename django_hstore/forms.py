try:
    import simplejson as json
except ImportError:
    import json

from django.forms import Field
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .widgets import AdminHStoreWidget
from . import utils


def validate_hstore(value):
    """ HSTORE validation """
    # if empty
    if value == '' or value == 'null':
        value = '{}'

    # ensure valid JSON
    try:
        # convert strings to dictionaries
        if isinstance(value, basestring):
            dictionary = json.loads(value)
        # if not a string we'll check at the next control if it's a dict
        else:
            dictionary = value
    except ValueError as e:
        raise ValidationError(_('Invalid JSON: %s') % e.message)

    # ensure is a dictionary
    if not isinstance(dictionary, dict):
        raise ValidationError(_('No lists or values allowed, only dictionaries'))

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


class DictionaryFieldWidget(JsonMixin, AdminHStoreWidget):
    pass


class ReferencesFieldWidget(JsonMixin, AdminHStoreWidget):

    def render(self, name, value, attrs=None):
        value = utils.serialize_references(value)
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
        return utils.unserialize_references(value)
