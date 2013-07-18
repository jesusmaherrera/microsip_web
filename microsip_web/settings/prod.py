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

MICROSIP_MODULES = (
    # Modules created for microsip and installed by default. You can add
    'microsip_web.apps.main',
    #'microsip_web.apps.main.filtros',
    'microsip_web.apps.inventarios',
    'microsip_web.apps.ventas',
    'microsip_web.apps.cuentas_por_pagar',
    #'microsip_web.apps.cuentas_por_cobrar',
    #'microsip_web.apps.contabilidad',
    #'microsip_web.apps.punto_de_venta',    
)
# Combine all the apps in the django variable INSTALLED_APPS
INSTALLED_APPS = DJANGO_APPS + MICROSIP_MODULES

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'C:\Microsip datos\AD2007(POLISAS)0_10.fdb', # Or path to database file if using sqlite3.
        'USER': 'SYSDBA',                      # Not used with sqlite3.
        'PASSWORD': 'masterkey',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {'charset':'ISO8859_1'},
    },
  
}

ROOT_URLCONF = 'microsip_web.urls.prod'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    (RUTA_PROYECTO + '/static/'),
)