import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'icenine.settings'

import django.core.handlers.wsgi
sys.path.append('C:/Inetpub/django/')
application = django.core.handlers.wsgi.WSGIHandler()
