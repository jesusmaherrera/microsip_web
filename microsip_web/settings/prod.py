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
INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES

ROOT_URLCONF = 'microsip_web.urls.prod'

# Additional locations of static files
STATICFILES_DIRS = (
    (RUTA_PROYECTO + '/static/'),
)