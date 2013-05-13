from common import *

DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.firebird', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3050',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS' : {'charset':'ISO8859_1'},
    },
  
}

# Additional locations of static files
STATICFILES_DIRS = (
    #'C:\wamp\www\microsip_web\static',
    #'C:\Users\Admin\Documents\GitHub\microsip_web\static',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    (RUTA_PROYECTO + '/static/'),
)