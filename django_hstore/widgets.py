from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.admin.templatetags.admin_static import static
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.conf import settings


__all__ = [
    'DefaultAdminHStoreWidget',
    'GrappelliHStoreWidget',
    'AdminHStoreWidget'
]


class DefaultAdminHStoreWidget(AdminTextareaWidget):
    pass


class GrappelliHStoreWidget(AdminTextareaWidget):
    """
    Widget that displays the HStore contents
    in a nice interactive admin UI for django-grappelli
    """
    @property
    def media(self):
        # load underscore from CDNJS (popular javascript content delivery network)
        external_js = [
            "//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.2/underscore-min.js"
        ]
        
        internal_js = [
            "django_hstore/hstore-grappelli-widget.js"
        ]
        
        js = external_js + [static("admin/js/%s" % path) for path in internal_js]
        
        return forms.Media(js=js)
    
    def render(self, name, value, attrs=None):
        # get default HTML from AdminTextareaWidget
        html = super(GrappelliHStoreWidget, self).render(name, value, attrs)
        
        # prepare template context
        template_context = Context({ 'field_name': name })
        # get template object
        template = get_template('hstore_grappelli_widget.html')
        # render additional html
        additional_html = template.render(template_context)
        
        # append additional HTML and mark as safe
        html = html + additional_html
        html = mark_safe(html)
        
        return html


if 'grappelli' in settings.INSTALLED_APPS:
    AdminHStoreWidget = GrappelliHStoreWidget
else:
    AdminHStoreWidget = DefaultAdminHStoreWidget