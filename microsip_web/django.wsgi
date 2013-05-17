import os, sys

sys.path.append('C:\wamp\www\microsip_web')
sys.path.append('C:\wamp\www')

os.environ['DJANGO_SETTINGS_MODULE'] = 'microsip_web.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()