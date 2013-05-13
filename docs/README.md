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

/////////////INTALAR PYTHON ////////////////////
7:Instalar python 2.7.3
8:Instalar setuptools-0.6c11.win32-py2.7
9: Agregar en variables de entorno en path ";C:\Python27;C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk;C:\Python27\Scripts;" o con "SET PATH=%PATH%;C:\Python27;C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk;C:\Python27\Scripts;"
10:copiar carpeta de pip-1.3 a escritorio e instalar pip de carpeta pip-1.3 con python setup.py install porar carpeta pip  de escritorio

/////////////INTALAR APLICACION Y LIBRERIAS NESESARIAS////////////////////
11:Instalar requerimentos de aplicacion con "pip install -r requirements.txt"
copiar carpeta de firebird de instaladores a C:\Python27\Lib\site-packages y C:\Python27\Lib\site-packages\django\db\backends

/////////////SYNCRONISAR BASE DE DATOS PYTHON ////////////////////
14:sincronizar base de datos con python manage.py syncdb
15:CONFIGURAR INICIADOR DE SERVIDOR CON IP Y RUTAS


////////////////////DEFINIR CAMPOS PARTICULARES PARA TABLAS//////////////////////////////
16:Definir campos particulares

PARA CUENTAS POR COBRAR

    class LibresCargosCC(models.Model):
        id            = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
        segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
        segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
        segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
        segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
        segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
        def __unicode__(self):
            return u'%s' % self.id
        class Meta:
            db_table = u'libres_cargos_cc'

    class LibresCreditosCC(models.Model):
        id            = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
        segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
        segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
        segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
        segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
        segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
        def __unicode__(self):
            return u'%s' % self.id
        class Meta:
            db_table = u'libres_creditos_cc'

PARA CUENTAS POR PAGAR

    class LibresCargosCP(models.Model):
        id                      = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
        segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
        segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
        segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
        segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
        segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
     	
     	def __unicode__(self):
            return u'%s' % self.id
        class Meta:
            db_table = u'libres_cargos_cp'

PARA VENTAS

    class LibresFacturasV(models.Model):
        id            = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
        segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
        segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
        segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
        segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
        segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    	
    	def __unicode__(self):
            return u'%s' % self.id
        class Meta:
            db_table = u'libres_fac_ve'

    class LibresDevFacV(models.Model):
        id            = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
        segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
        segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
        segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
        segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
        segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
        
        def __unicode__(self):
            return u'%s' % self.id
        class Meta:
            db_table = u'libres_devfac_ve'

17) LISTO


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


############# APLICACION DE PUNTOS###############################
Cada ves que se agrege un detalla a una venta se agreggran sus puntos:

Instalacion:
    1:Agregar en las tablas (articulos, lineas_articulos, grupos_lineas, clientes, doctos_pv_det(*smallint)) un campo entergo con nombre "PUNTOS" Y "DINERO_ELECTRONICO"
    2:Agregar trigers
        a) /setup/triggers/DOCTOS_PV_DET_AI_PUNTOS a tabla doctos_pv_det como "AFTER INSERT"
        b) /setup/triggers/DOCTOS_PV_COBROS_BI_PUNTOS a tabla doctos_pv_det como "BEFOR INSERT" 
