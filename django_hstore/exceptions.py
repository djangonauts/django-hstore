from __future__ import unicode_literals, absolute_import


class HStoreDictException(Exception):
    json_error_message = None

    def __init__(self, *args, **kwargs):
        self.json_error_message = kwargs.pop('json_error_message', None)
        super(HStoreDictException, self).__init__(*args, **kwargs)
