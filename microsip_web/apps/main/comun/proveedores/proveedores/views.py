#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from microsip_web.apps.inventarios.models import *
from django.db.models.query import EmptyQuerySet

from forms import *

import json
from decimal import *


import datetime, time
from django.db.models import Q
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from microsip_web.apps.inventarios.views import c_get_next_key
from microsip_web.libs import contabilidad
from microsip_web.apps.cuentas_por_cobrar import forms as formsCC
from microsip_web.apps.cuentas_por_cobrar import models as modelsCC
from microsip_web.libs.custom_db.main import get_conecctionname

##########################################
##                                      ##
##            Proveedores               ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def proveedores_view(request, template_name='cuentas_por_pagar/catalogos/proveedores/proveedores.html'):
    provedores_list = Proveedor.objects.all()

    paginator = Paginator(provedores_list, 15) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        proveedores = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        proveedores = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        proveedores = paginator.page(paginator.num_pages)

    c = {'proveedores':proveedores}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def proveedor_manageView(request, id = None, template_name='cuentas_por_pagar/catalogos/proveedores/proveedor.html'):
    message = ''

    if id:
        proveedor = get_object_or_404(Proveedor, pk=id)
    else:
        proveedor = Proveedor()

    if request.method == 'POST':
        form = ProveedorManageForm(request.POST, instance= proveedor)
        if form.is_valid():
            proveedor = form.save(commit=False)
            if not proveedor.id > 0:
                proveedor.id=-1
            proveedor.estado = proveedor.ciudad.estado
            proveedor.pais = proveedor.estado.pais
            proveedor.save()
    else:
        form = ProveedorManageForm(instance=proveedor)

    c = {'form':form}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def tipos_proveedores_view(request, template_name='cuentas_por_pagar/catalogos/tipos_proveedores/tipos_proveedores.html'):
    tipos_provedores_list = ProveedorTipo.objects.all()

    paginator = Paginator(tipos_provedores_list, 15) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        tipos_proveedores = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tipos_proveedores = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tipos_proveedores = paginator.page(paginator.num_pages)

    c = {'tipos_proveedores':tipos_proveedores}
    return render_to_response(template_name, c, context_instance=RequestContext(request))