 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect

from django.template import RequestContext

from decimal import *
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
    return HttpResponseRedirect('/')

def ventas_inicializar_tablas():
    c = connection.cursor()
    c.execute(procedures['ventas_inicializar'])
    c.execute("EXECUTE PROCEDURE ventas_inicializar;")
    transaction.commit_unless_managed()

def punto_de_venta_inicializar_tablas():
    c = connection.cursor()
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
    