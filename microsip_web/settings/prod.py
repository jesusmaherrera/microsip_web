from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'autocomplete_light',
    'dajaxice',
)

# Combine all the apps in the django variable INSTALLED_APPS
MICROSIP_PLUGINS_APPS = ()
for microsip_app in MICROSIP_PLUGINS:
    MICROSIP_PLUGINS_APPS += (microsip_app['app'],)

INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES + MICROSIP_PLUGINS_APPS

ROOT_URLCONF = 'microsip_web.urls.prod'

# Additional locations of static files
STATICFILES_DIRS = (
    (RUTA_PROYECTO + '/static/'),
)