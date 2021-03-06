 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from decimal import *
from microsip_web.libs.custom_db.procedures import procedures
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ...libs.api.models import *
from forms import *

import datetime, time
from django.db import connections, transaction
# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core import management
import fdb
from microsip_web.settings.local_settings import MICROSIP_MODULES, MICROSIP_PLUGINS
from microsip_web.apps.inventarios.triggers import triggers as inventarios_triggers
from microsip_web.apps.inventarios.triggers_salidas import triggers_salidas as inventarios_triggers_salidas

from microsip_web.libs.custom_db.main import first_or_none
from django.db.utils import DatabaseError

try:
    scripts = AplicationPlugin.objects.all()
    for script in scripts:
        __import__('microsip_web.data.plugins.%s'%script.name)
except django.db.DatabaseError:
    pass

@login_required( login_url = '/login/' )
def AplicationPluginDelete( request, id=None):
    """ Borrar el registro de un plugin  """
    plugin = AplicationPlugin.objects.get(pk=id)
    plugin.delete()
    return HttpResponseRedirect( '/plugins/' )

@login_required( login_url = '/login/' )
def AplicationPluginsView( request, template_name = 'main/plugins/plugins.html' ):
    """ Lista de scripts  """

    c = { 'plugins' : AplicationPlugin.objects.all() }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required(login_url='/login/')
def AplicationPluginManageView( request, id = None, template_name = 'main/plugins/plugin.html' ):

    message = ''

    if id:
        plugin = get_object_or_404( AplicationPlugin, pk = id)
    else:
        plugin =  AplicationPlugin()

    form = AplicationPluginForm( request.POST or None, instance =  plugin )            
    if form.is_valid():
        grupo = form.save()
        return HttpResponseRedirect( '/plugins/' )
    

    c = { 'form' : form, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )
    
@login_required( login_url = '/login/' )
def conexiones_View( request, template_name = 'main/conexiones/conexiones.html' ):
    """ Lista de conexiones a carpetas ( Microsip Datos ). """

    c = { 'conexiones' : ConexionDB.objects.all() }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required(login_url='/login/')
def conexion_manageView( request, id = None, template_name = 'main/conexiones/conexion.html' ):
    """ Lista de conexiones """

    message = ''
    initial_form = None
    if id:
        conexion = get_object_or_404( ConexionDB, pk = id)
    else:
        conexion =  ConexionDB()
        initial_form = {
        'nombre':'local',
        'tipo':'L',
        'servidor':'localhost',
        'carpeta_datos':'C:\Microsip datos',
        'usuario':'SYSDBA'
        }

    form = ConexionManageForm( request.POST or None, instance=conexion, initial=initial_form)
    
    if form.is_valid():
        grupo = form.save()
        return HttpResponseRedirect( '/conexiones/' )

    c = { 'form' : form, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required( login_url = '/login/' )
def inicializar_tablas( request ):
    """ Agrega trigers y campos nuevos en tablas de base de datos. """

    #ventas_inicializar_tablas()
    if request.user.is_superuser:

        basedatos_activa = request.session[ 'selected_database' ]
        if basedatos_activa == '':
            return HttpResponseRedirect( '/select_db/' )
        else:
            conexion_activa_id = request.session[ 'conexion_activa' ]
            
        conexion_name = "%02d-%s"%( conexion_activa_id, basedatos_activa )
        

        # Campos nuevos en tablas
        sincronizar_tablas( conexion_name = conexion_name )
        
        if 'microsip_web.apps.punto_de_venta' in MICROSIP_MODULES:
            if not Registry.objects.filter( nombre = 'ARTICULO_VENTAS_FG_PV_ID' ).exists():
                padre = first_or_none(Registry.objects.filter(nombre='PreferenciasEmpresa'))
                if padre:
                    Registry.objects.create(
                            nombre = 'ARTICULO_VENTAS_FG_PV_ID',
                            tipo = 'V',
                            padre = padre
                        ) 

        if 'microsip_web.apps.inventarios' in MICROSIP_MODULES:
            actualizar_triggers_inventarios( conexion_name = conexion_name )
        else:
            borrar_triggers_inventarios( conexion_name = conexion_name )

        #cuentas_por_pagar_inicializar_tablas()
        #cuentas_por_cobrar_inicializar_tablas()

        management.call_command( 'syncdb', database = conexion_name )

    return HttpResponseRedirect('/')


def sincronizar_tablas( conexion_name = None ):
    """ Modifica todas las tablas con campos nuevos para uso en aplicacion. """
    c = connections[ conexion_name ].cursor()
    try:
        c.execute("DELETE FROM DJANGO_CONTENT_TYPE;")
    except DatabaseError:
        pass
    
   
    import importlib

    for plugin in MICROSIP_PLUGINS:
        plugin_procedures = None
        path = plugin['app']+'.procedures'
        try:
            plugin_procedures_module = importlib.import_module(plugin['app']+'.procedures')
        except ImportError:
            pass
        else:
            plugin_procedures = plugin_procedures_module.procedures

        if plugin_procedures:
            for procedure in plugin_procedures.keys():
                c.execute( plugin_procedures[procedure] )
                c.execute('EXECUTE PROCEDURE %s;'%procedure)
                c.execute('DROP PROCEDURE %s;'%procedure)

    ################## STRORE PROCEDURES ###################
    if 'microsip_web.apps.main.comun.articulos.articulos.alertas' in MICROSIP_MODULES:
        from microsip_web.apps.main.comun.articulos.articulos.alertas.procedures import procedures as alertas_procedures
        for procedure in alertas_procedures.keys():
            c.execute( alertas_procedures[procedure] )
            c.execute('EXECUTE PROCEDURE %s;'%procedure)
            c.execute('DROP PROCEDURE %s;'%procedure)

    #lbres clientes
    c.execute( procedures[ 'SIC_LIBRES_CLIENTES_AT' ] ) 
    c.execute('EXECUTE PROCEDURE SIC_LIBRES_CLIENTES_AT;')
    c.execute('DROP PROCEDURE SIC_LIBRES_CLIENTES_AT;')

    c.execute( procedures[ 'SIC_FILTROS_ARTICULOS_AT' ] )
    c.execute('EXECUTE PROCEDURE SIC_FILTROS_ARTICULOS_AT;')   
    c.execute('DROP PROCEDURE SIC_FILTROS_ARTICULOS_AT;')   

    #inventarios

    c.execute( procedures['SIC_DOCTOSINDET_AT'] )
    c.execute("EXECUTE PROCEDURE SIC_DOCTOSINDET_AT;")
    c.execute("DROP PROCEDURE SIC_DOCTOSINDET_AT;")

    c.execute( procedures['SIC_ALMACENES_AT'] )
    c.execute("EXECUTE PROCEDURE SIC_ALMACENES_AT;")
    c.execute("DROP PROCEDURE SIC_ALMACENES_AT;")

    transaction.commit_unless_managed()

def ventas_inicializar_tablas( conexion_name = None ):
    """ Agrega campos particulares para segmentos """

    c = connections[ conexion_name ].cursor()
    c.execute( procedures[ 'ventas_inicializar' ] )
    c.execute( "EXECUTE PROCEDURE ventas_inicializar;" )
    transaction.commit_unless_managed()

def actualizar_triggers_inventarios( conexion_name = None ):
    """ Agrega trigger a base de datos para aplicacion inventarios. """

    c = connections[ conexion_name ].cursor()
    ####################### TRIGGERS #######################
    c.execute( inventarios_triggers[ 'SIC_PUERTA_INV_DOCTOSIN_BU' ] )
    transaction.commit_unless_managed()

def borrar_triggers_inventarios( conexion_name = None ):
    """ Borra los triggers de inventarios """

    c = connections[conexion_name].cursor()

    c.execute( procedures[ 'SIC_PUERTA_DEL_TRIGGERS' ] )
    c.execute('EXECUTE PROCEDURE SIC_PUERTA_DEL_TRIGGERS;')
    c.execute('drop PROCEDURE SIC_PUERTA_DEL_TRIGGERS;')

    transaction.commit_unless_managed()

def cuentas_por_pagar_inicializar_tablas( conexion_name = None ):
    """ Agrega campos particulares para segmentos """

    c = connections[conexion_name].cursor()
    c.execute(procedures['cuentas_por_pagar_inicializar'])
    c.execute('EXECUTE PROCEDURE cuentas_por_pagar_inicializar;')
    transaction.commit_unless_managed()

def cuentas_por_cobrar_inicializar_tablas( conexion_name = None ):
    """ Agrega campos particulares para segmentos """

    c = connections[conexion_name].cursor()
    c.execute(procedures['cuentas_por_cobrar_inicializar'])
    c.execute("EXECUTE PROCEDURE cuentas_por_cobrar_inicializar;")
    transaction.commit_unless_managed()

@login_required( login_url = '/login/' )
def index( request ):
    return render_to_response( 'main/index.html',{}, context_instance = RequestContext( request ) )
    