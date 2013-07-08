
from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#DATABASE_ROUTERS = ['inventarios.router.MicrosipRouter']
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'database',                      # Or path to database file if using sqlite3.
    #     'USER': '',                      # Not used with sqlite3.
    #     'PASSWORD': '',                  # Not used with sqlite3.
    #     'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    # },
    'default': {
       'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
       #D2007(POLISAS)0_9
        #'NAME': 'C:\Microsip datos\AD2007(POLISAS)0_9.fdb', # Or path to database file if using sqlite3.
        #D2007(POLISAS)0_10
        #'NAME': 'C:\Microsip datos\PRUEBAS.fdb',
        'NAME': 'C:\Microsip datos\AD2007(POLISAS)0_10.fdb',
        #'NAME': 'C:\Microsip datos\ESSEX WELD SOLUTIONS.fdb', # Or path to database file if using sqlite3.
        #RAFISA
        #'NAME': 'C:\Microsip datos\RAFISA.fdb', # Or path to database file if using sqlite3.
        #ESSEX
        #'NAME': 'C:\Microsip datos\ESSEX.fdb', # Or path to database file if using sqlite3.
        'USER': 'SYSDBA',                      # Not used with sqlite3.
        'PASSWORD': 'masterkey',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {'charset':'ISO8859_1'},
    },
    # 'db_chuy': {
    #    'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #     'NAME': 'C:\Microsip datos\ESSEX454.fdb', # Or path to database file if using sqlite3.
    #     'USER': 'SYSDBA',                      # Not used with sqlite3.
    #     'PASSWORD': 'masterkey',                  # Not used with sqlite3.
    #     'HOST': 'cuenta.noip.org',                      # Set to empty string for localhost. Not used with sqlite3.
    #     'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
    #     'OPTIONS' : {'charset':'ISO8859_1'},
    # },
}

ROOT_URLCONF = 'microsip_web.urls.dev'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    (RUTA_PROYECTO + '/static/'),
)
