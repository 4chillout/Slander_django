"""
WSGI config for Slander project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application


path = '/home/4chillout/.virtualenvs/4chillout.pythonanywhere.com/'
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Slander.settings')
application = get_wsgi_application()
