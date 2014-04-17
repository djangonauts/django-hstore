from __future__ import unicode_literals, absolute_import

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.admin.templatetags.admin_static import static
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.conf import settings


__all__ = [
    'AdminHStoreWidget'
]


class BaseAdminHStoreWidget(AdminTextareaWidget):
    """
    Base admin widget class for default-admin and grappelli-admin widgets
    """
    admin_style = 'default'

    @property
    def media(self):
        # load underscore from CDNJS (popular javascript content delivery network)
        external_js = [
            "//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.2/underscore-min.js"
        ]

        internal_js = [
            "django_hstore/hstore-widget.js"
        ]

        js = external_js + [static("admin/js/%s" % path) for path in internal_js]

        return forms.Media(js=js)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        # it's called "original" because it will be replaced by a copy
        attrs['class'] = 'hstore-original-textarea'

        # get default HTML from AdminTextareaWidget
        html = super(BaseAdminHStoreWidget, self).render(name, value, attrs)

        # prepare template context
        template_context = Context({
            'field_name': name,
            'STATIC_URL': settings.STATIC_URL
        })
        # get template object
        template = get_template('hstore_%s_widget.html' % self.admin_style)
        # render additional html
        additional_html = template.render(template_context)

        # append additional HTML and mark as safe
        html = html + additional_html
        html = mark_safe(html)

        return html


class DefaultAdminHStoreWidget(BaseAdminHStoreWidget):
    """
    Widget that displays the HStore contents
    in the default django-admin with a nice interactive UI
    """
    admin_style = 'default'


class GrappelliAdminHStoreWidget(BaseAdminHStoreWidget):
    """
    Widget that displays the HStore contents
    in the django-admin with a nice interactive UI
    designed for django-grappelli
    """
    admin_style = 'grappelli'


if 'grappelli' in settings.INSTALLED_APPS:
    AdminHStoreWidget = GrappelliAdminHStoreWidget
else:
    AdminHStoreWidget = DefaultAdminHStoreWidget
