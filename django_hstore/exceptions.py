"""
django_hstore.exceptions
"""


class HStoreDictionaryException(Exception):
    
    json_error_message = None
    
    def __init__(self, *args, **kwargs):
        
        self.json_error_message = kwargs.pop('json_error_message', None)
        
        super(self.__class__, self).__init__(*args, **kwargs)