## Descripción
**Inventario físico a puerta abierta** es una herramienta para el apoyo a la hora de realizar un inventario físico **en Microsip** sin necesidad de cerrar la empresa.

El inventario fisico lo puede realizar con con **cualquier dispositivo que tenga un explorador web** _(smart phone,tablet, ipod, ipad, laptop, o con una terminal con lector de código de barras)_.

![pantalla de inventario fisico](https://fbcdn-sphotos-e-a.akamaihd.net/hphotos-ak-frc3/1269640_589440644431008_338792098_o.jpg)
![Inventario físico mobile](https://fbcdn-sphotos-g-a.akamaihd.net/hphotos-ak-ash3/602930_589443801097359_1377843750_n.jpg)
## Funcionamiento
### Aplicación Web

**Seleccionar artículos a inventariar**

lo puede hacer ya sea **por medio de alguna clave del articulo** o por el **nombre del articulo** 
al momento de seleccionar un articulo en el inventario si este articulo ya se a inventariado nos mostrara un mensaje de los detalles de este como que usuario, donde y que cantidad de unidades puso **[SYSDBA/Estante1=100]**:

![detalles articulo](https://scontent-a-lax.xx.fbcdn.net/hphotos-ash3/598877_589449747763431_479784911_n.jpg)

El filtro por nombre de articulo es por medio de una auto-completado el cual conforme va escribiendo el nombre del articulo, los artículos de microsip se van filtrando.

![fIltro por articulo](https://scontent-b-lax.xx.fbcdn.net/hphotos-prn2/p480x480/1375691_589451821096557_570111113_n.jpg)

### Aplicación **Microsip**

Dentro de la aplicación Microsip **cualquier** movimiento que tenga que ver con inventarios ya sean _compra, venta, traspaso de almacén, etc._ afectara a nuestro inventario físico abierto desde el momento en que se cree el inventario físico abierto hasta que este mismo se aplique.

> Si capturo **10 artículos(lápiz)** en inventario físico y posteriormente hago la venta de **5 artículos(lápiz)** en el inventario físico automáticamente se me van a rebajar esos últimos 5 artículos.

> Si posteriormente realizo una compra de 6 artículos(lápiz) como resultado en mi inventario tendré **11 artículos(lápiz)**

## Importante
Para un mejor resultado al momento de realizar un inventario físico es de vital importancia tomar en cuanta los siguientes puntos.

* En el periodo que se realice el inventario es necesario **separar las compras  y devoluciones**
* En caso de tener el mismo articulo en varios estantes (**comunicar al personal de ventas para que tome los artículos del estante donde ya se contaron** si es el caso en que ya se contaron [si no se an contado no hay problema la aplicación ignorara estos])



microsip_web
============

/////////////RESPALDAR/////////////////
1:Respaldar microsip app
2:Respaldar microsip bases de datos
3:Respaldar firebird Y microsip de archivos de programa

///////////// INTALAR APLICACION ////////////////////
1) Ejecutar setup de la carpeta "instalador microsip apps" [con permisos de administrador]

///////////// CONFIGURACION ////////////////////
1) Configurar conexion a base de datos "C:\microsip_web_compilado\microsip_web\settings\prod.py
2) Ejecutar archivo "C:\microsip_web_compilado\actualizar.lnk  
3) configurar ip de servidor en archivo "C:\microsip_web_compilado\extras\scripts\Iniciar microsip app.cmd"
4) Ejecutar <ip:puerto>/inicializar_tablas para inicializar tablas
5) Listo


ACTUALIZACION DE APLICACION




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
        - x...                                      A               C
    -Credito
        - Al 16                                     A               C
        - Al 0                                      A               C
        - Ambos                                     A               C
        - x...                                      A               C
IVA
    - Contado (IVA efectivo cobrado)                A               C
    - Credito (IVA pendiente cobrar)                A               C
    - Ambos                                         A               C

SEGMENTOS (etc...)                                 C-A             C-A

////////////////////////////PLANTILLAS DE CUENTAS POR PAGAR, COMPRAS ////////////////////////////////

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


git update-index --assume-unchanged manage.py
