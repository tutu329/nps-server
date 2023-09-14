"""
WSGI config for nps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import threading

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nps.settings')
# print("in wsgi.py thread is : \"{}\"".format(threading.current_thread().name))

application = get_wsgi_application()
