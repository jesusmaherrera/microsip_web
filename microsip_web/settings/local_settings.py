DATABASES = {
    'default': {
       'ENGINE': 'django.db.backends.firebird', 
        'NAME': 'C:\Microsip datos\NOMBRE_BASEDEDATOS.fdb',
        'USER': 'SYSDBA', 
        'PASSWORD': 'masterkey',
        'HOST': 'localhost',
        'PORT': '3050',
        'OPTIONS' : {'charset':'ISO8859_1'},
    },
}

MICROSIP_MODULES = (
    'microsip_web.apps.main',
    #'microsip_web.apps.main.filtros',
    #'microsip_web.apps.inventarios',
    #'microsip_web.apps.ventas',
    #'microsip_web.apps.cuentas_por_pagar',
    #'microsip_web.apps.cuentas_por_cobrar',
    #'microsip_web.apps.contabilidad',
    #'microsip_web.apps.punto_de_venta',    
)