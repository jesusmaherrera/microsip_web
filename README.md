microsip_web
============

INSTALACION DE APLICACION

/////////////RESPALDAR/////////////////
1:Respaldar microsip app
2:Respaldar microsip bases de datos
3:Respaldar firebird de archivos de programa

/////////////REINSTALAR FIREBIRD/////////////////
4:detener firebird en services o servicios
5:Desinstalar Firebird poner no nada borrar archivos
6:Reinstalar firbird Server **poner no nada borrar archivos** (EN INSTALCION INDICAR Copiar la libreria cliente de firebird al directorio<system>)

/////////////INTALAR APLICACION////////////////////
7:Agregar en variables de entorno en path ";C:\Python27;C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk;C:\Python27\Scripts;" o con [setx PATH "%PATH%;C:\Python27;C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk;C:\Python27\Scripts"]
8:Descromprimir archivo instaladores_microsip_web en c:/instaladores_microsip_web
9:En carpeta descomprimida ejecutar instaladores segun estan numerados ejemplo "1)Nombre de instaldor" asta el cuatro
10: Configurar conexion a base de datos "C:\microsip_web_compilado\microsip_web\settings\prod.py

/////////////CONFIGURAR Y SYNCRONISAR BASE DE DATOS////////////////////
11:sincronizar base de datos con python manage.py syncdb
12:configurar ip de servidor en archivo "C:\microsip_web_compilado\extras\scripts\Iniciar microsip app.cmd"
13:Ejecutar aplicacion con ip:puerto indicados anteriormente
14: ejecutar <ip:puerto>/inicializar_tablas para inicializar tablas
15:listo

ACTUALIZACION DE APLICACION

1: Ejecutar archivo "C:\microsip_web_compilado\actualizar.lnk


CONFIGURACION EN APACHE

Primero que nada es necesario instalar apache (xampserver)

1)Descargar el modulo mod_wsgi de "http://code.google.com/p/modwsgi/downloads/list" y gurdarlo en la rota "C:\wamp\bin\apache\apache2.2.22\modules"
  Agregar la siguiente inea de configuracion en apache 
  LoadModule wsgi_module modules/mod_wsgi.so

2) Agregar estas lineas al archivo de configuracion de apache 
  
  WSGIScriptAlias / "C:/wamp/www/microsip_web/microsip_web/django.wsgi"
  Alias /static/ C:/wamp/www/microsip_web/inventarios/static/

AUTOCOMPLETE

Documentacion en: http://django-autocomplete-light.rtfd.org

Repocitorio en github https://github.com/yourlabs/django-autocomplete-light


1) Instalar el paquete con django-autocomplete-light:
	pip install django-autocomplete-light

2) En carpeta static copiar carpeta autocomplete_light de css y js

3) En carpeta templetes copiar carpeta autocomplete_light de templetes

4) Agregar archivo autocomplete_light_registry.py a carpeta de aplicacion

5) En formulario donde se desee aplicar poner el codigo segun el modelo a usar (archivo forms.py):
	#agregar al primcipio del archivo
	import autocomplete_light
	#agregar despues de class Meta:
  	"widgets = autocomplete_light.get_widgets_dict(DoctosInvfisDet)"





I guess a test would be to install a package with pip using a --index-url=file:////localhost/c$/some/package/index where /index contains subdirectories of projects:

/index
/pkg
/pkg-0.0.1.tar.gz
The pip command: pip install --index-url=file:////localhost/c$/some/package/index pkg should find and install pkg-0.0.1.tar.gz.

MIGRATIONS

Follow these steps:

Export your data to a fixture using the dumpdata management command
Drop the table
Run syncdb
Reload your data from the fixture using the loaddata management command


PLANTILLAS

//////////////////////////////// PLANTILLAS DE VENTAS, CUENTAS POR COBRAR, Y PUNTO DE VENTA /////////////////////////////////////

                                                FACTURAS      DEVOLUCIONES
Clientes                                            C               A     

Bancos                                              C               A

Descuentos                                          C               A

ventas
    -Ambos                                          A               C
    -Contado
        - Al 16                                     A               C
        - Al 0                                      A               C
        - Ambos                                     A               C
    -Credito
        - Al 16                                     A               C
        - Al 0                                      A               C
        - Ambos                                     A               C
IVA
    - Contado (IVA efectivo cobrado)                A               C
    - Credito (IVA pendiente cobrar)                A               C
    - Ambos                                         A               C

SEGMENTOS (etc...)                                 C-A             C-A

////////////////////////////PLANTILLAS DE CUENTAS POR PAGAR////////////////////////////////

Proveedores                                         A

Bancos                                              A

Descuentos                                          C

Compras                                             C
    -Ambos
    -Contado                                        C
        - Al 16                                     C
        - Al 0                                      C
        - Ambos                                     C
    -Credito                                        C
        - Al 16                                     C
        - Al 0                                      C
        - Ambos                                     C
IVA
    - Contado (IVA efectivo pagado)                 C
    - Credito (IVA pendiente pagar)                 C
    - Ambos                                         C    

SEGMENTOS (Fletes, etc...)                         C-A


//////PUNTO DE VENTA////////////////////
TIPOS DE POLIZAS 
ventas                      :Ingresos
devoluciones                :Diario
Cobros cuentas por cobrar   :Ingresos
