"""
WSGI config for testproj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproj.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
