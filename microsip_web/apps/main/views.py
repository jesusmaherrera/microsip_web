 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from decimal import *
from microsip_web.libs.custom_db.procedures import procedures
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import *
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
from microsip_web.settings.common import MICROSIP_MODULES
from microsip_web.apps.inventarios.triggers import triggers as inventarios_triggers
from microsip_web.apps.punto_de_venta.triggers import triggers as punto_de_venta_triggers

@login_required(login_url='/login/')
def conexiones_View(request, template_name='main/conexiones/conexiones.html'):
    c = {'conexiones':ConexionDB.objects.all()}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def conexion_manageView(request, id = None, template_name='main/conexiones/conexion.html'):
    message = ''

    if id:
        conexion = get_object_or_404( ConexionDB, pk=id)
    else:
        conexion =  ConexionDB()
        
    if request.method == 'POST':
        form = ConexionManageForm(request.POST, instance=  conexion)
        if form.is_valid():
            grupo = form.save()
            return HttpResponseRedirect('/conexiones/')
    else:
        form = ConexionManageForm(instance= conexion)

    c = {'form':form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def reiniciar_servidor(request):
    if request.user.is_superuser:
        management.call_command("runserver", noreload=True)
    return HttpResponseRedirect('/')

@login_required(login_url='/login/')
def inicializar_tablas(request):
    #ventas_inicializar_tablas()
    if request.user.is_superuser:
        basedatos_activa = request.user.userprofile.basedatos_activa
        if basedatos_activa == '':
            return HttpResponseRedirect('/select_db/')
        else:
            conexion_activa_id = request.user.userprofile.conexion_activa.id

        conexion_name = "%02d-%s"%(conexion_activa_id, basedatos_activa)
        
        quitar = False
        if 'microsip_web.apps.punto_de_venta' in MICROSIP_MODULES:
            punto_de_venta_actualizar_tablas( conexion_name = conexion_name )
        else:
            quitar = True

        if 'microsip_web.apps.inventarios' in MICROSIP_MODULES:
            inventario_actualizar_tablas( conexion_name = conexion_name )
        else:
            quitar = True

        #cuentas_por_pagar_inicializar_tablas()
        #cuentas_por_cobrar_inicializar_tablas()

        #Sincronizar todas las bases de datos de microsip con tablas de la aplicacion
        
        management.call_command('syncdb', database=conexion_name)

    return HttpResponseRedirect('/')

def inventario_actualizar_tablas( conexion_name = None ):
    c = connections[conexion_name].cursor()
    ################## STRORE PROCEDURES ###################
    c.execute(procedures['SIC_DOCTOINVFISDET_AT'])
    c.execute("EXECUTE PROCEDURE SIC_DOCTOINVFISDET_AT;")
    ####################### TRIGGERS #######################
    c.execute(inventarios_triggers['SIC_PUERTA_INV_DESGLOSEDIS_AI'])
    c.execute(inventarios_triggers['SIC_PUERTA_INV_DOCTOSINDET_BI'])
    c.execute(inventarios_triggers['SIC_PUERTA_INV_DOCTOSINDET_BD'])
    c.execute(inventarios_triggers['SIC_PUERTA_INV_DOCTOSIN_BU'])

    transaction.commit_unless_managed()

def ventas_inicializar_tablas( conexion_name = None ):
    c = connections[conexion_name].cursor()
    c.execute(procedures['ventas_inicializar'])
    c.execute("EXECUTE PROCEDURE ventas_inicializar;")
    transaction.commit_unless_managed()

def punto_de_venta_actualizar_tablas( conexion_name = None ):
    c = connections[conexion_name].cursor()
    ################## STRORE PROCEDURES ###################
    c.execute(procedures['SIC_PUNTOS_ARTICULOS_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_ARTICULOS_AT;')

    c.execute(procedures['SIC_PUNTOS_LINEASARTICULOS_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_LINEASARTICULOS_AT;')
    
    c.execute(procedures['SIC_PUNTOS_GRUPOSLINEAS_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_GRUPOSLINEAS_AT;')
    
    #Clientes
    c.execute(procedures['SIC_PUNTOS_CLIENTES_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_CLIENTES_AT;')

    c.execute(procedures['SIC_PUNTOS_LIBRESCLIENTES_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_LIBRESCLIENTES_AT;')
    
    c.execute(procedures['SIC_PUNTOS_TIPOSCLIENTES_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_TIPOSCLIENTES_AT;')

    c.execute(procedures['SIC_PUNTOS_DOCTOSPVDET_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_DOCTOSPVDET_AT;')
    
    c.execute(procedures['SIC_PUNTOS_DOCTOS_PV_AT'])
    c.execute('EXECUTE PROCEDURE SIC_PUNTOS_DOCTOS_PV_AT;')

    #lbres clientes
    c.execute(procedures['SIC_LIBRES_CLIENTES_AT']) 
    c.execute('EXECUTE PROCEDURE SIC_LIBRES_CLIENTES_AT;')

    c.execute(procedures['SIC_FILTROS_ARTICULOS_AT'])
    c.execute('EXECUTE PROCEDURE SIC_FILTROS_ARTICULOS_AT;')    
    ####################### TRIGGERS #######################
     #DETALLE DE VENTAS
    c.execute(punto_de_venta_triggers['SIC_PUNTOS_PV_DOCTOSPVDET_BU'])
    c.execute(punto_de_venta_triggers['SIC_PUNTOS_PV_DOCTOSPVDET_AD'])
    #VENTAS
    c.execute(punto_de_venta_triggers['SIC_PUNTOS_PV_DOCTOSPV_BU'])
    c.execute(punto_de_venta_triggers['SIC_PUNTOS_PV_DOCTOSPV_AD'])
    #CLIENTES
    c.execute(punto_de_venta_triggers['SIC_PUNTOS_PV_CLIENTES_BU'])
    #EXCEPTION
    try:
        c.execute(
        '''
        CREATE EXCEPTION EX_CLIENTE_SIN_SALDO 'El cliente no tiene suficiente saldo';   
        ''')
    except Exception, e:
       temp = 0

    transaction.commit_unless_managed()

def cuentas_por_pagar_inicializar_tablas( conexion_name = None ):
    c = connections[conexion_name].cursor()
    c.execute(procedures['cuentas_por_pagar_inicializar'])
    c.execute('EXECUTE PROCEDURE cuentas_por_pagar_inicializar;')
    transaction.commit_unless_managed()

def cuentas_por_cobrar_inicializar_tablas( conexion_name = None ):
    c = connections[conexion_name].cursor()
    c.execute(procedures['cuentas_por_cobrar_inicializar'])
    c.execute("EXECUTE PROCEDURE cuentas_por_cobrar_inicializar;")
    transaction.commit_unless_managed()

@login_required(login_url='/login/')
def index(request):
    return render_to_response('main/index.html', {}, context_instance=RequestContext(request))
    