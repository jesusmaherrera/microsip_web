 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from django.template import RequestContext

from decimal import *
from microsip_web.libs.custom_db.triggers import triggers
from microsip_web.libs.custom_db.procedures import procedures

from models import *
from forms import *

import datetime, time
from django.db import connection, transaction
# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

def inicializar_tablas(request):
    #ventas_inicializar_tablas()
    punto_de_venta_inicializar_tablas()
    #cuentas_por_pagar_inicializar_tablas()
    #cuentas_por_cobrar_inicializar_tablas()
    inventarios_agregar_trigers()
    punto_de_venta_agregar_trigers()
    return HttpResponseRedirect('/')

def inventarios_agregar_trigers():
    c = connection.cursor()
    #ENTRADAS Y SALIDAS DE INVENTARIOS
    c.execute(triggers['DOCTOS_IN_DET_BI_PUERTA_ABIERTA'])
    c.execute(triggers['DOCTOS_IN_DET_BD_PUERTA_ABIERTA'])
    c.execute(triggers['DOCTOS_IN_BU_PUERTA_ABIERTA'])
    c.execute(triggers['DESGLOSE_EN_DISCRETOS_AI_PUERTA'])
    
    transaction.commit_unless_managed()

def punto_de_venta_agregar_trigers():
    c = connection.cursor()
    #DETALLE DE VENTAS
    c.execute(triggers['DOCTOS_PV_DET_BU_PUNTOS'])
    c.execute(triggers['DOCTOS_PV_DET_AD_PUNTOS'])
    #VENTAS
    c.execute(triggers['DOCTOS_PV_BU_PUNTOS'])
    c.execute(triggers['DOCTOS_PV_AD_PUNTOS'])
    #CLIENTES
    c.execute(triggers['CLIENTES_BU_PUNTOS'])
    #EXCEPTION
    try:
        c.execute(
        '''
        CREATE EXCEPTION EX_CLIENTE_SIN_SALDO 'El cliente no tiene suficiente saldo';   
        ''')
    except Exception, e:
       print "Oops!  No pudo agregarse la excepción EX_CLIENTE_SIN_SALDO por que esta ya existe. "

    transaction.commit_unless_managed()

def ventas_inicializar_tablas():
    c = connection.cursor()
    c.execute(procedures['ventas_inicializar'])
    c.execute("EXECUTE PROCEDURE ventas_inicializar;")
    transaction.commit_unless_managed()

def punto_de_venta_inicializar_tablas():
    c = connection.cursor()
    c.execute(procedures['punto_de_venta_inicializar_t'])
    c.execute('EXECUTE PROCEDURE punto_de_venta_inicializar_t;')
    transaction.commit_unless_managed()

def cuentas_por_pagar_inicializar_tablas():
    c = connection.cursor()
    c.execute(procedures['cuentas_por_pagar_inicializar'])
    c.execute('EXECUTE PROCEDURE cuentas_por_pagar_inicializar;')
    transaction.commit_unless_managed()

def cuentas_por_cobrar_inicializar_tablas():
    c = connection.cursor()
    c.execute(procedures['cuentas_por_cobrar_inicializar'])
    c.execute("EXECUTE PROCEDURE cuentas_por_cobrar_inicializar;")
    transaction.commit_unless_managed()

@login_required(login_url='/login/')
def index(request):
    return render_to_response('main/index.html', {}, context_instance=RequestContext(request))
    