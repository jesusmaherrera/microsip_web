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
##        Generacion de polizas         ##
##                                      ##
##########################################

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_documentos_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla='', descripcion= '', connection_name='', usuario_micorsip=''):
    
    depto_co = ContabilidadDepartamento.objects.get(clave='GRAL')
    error   = 0
    msg     = ''
    documentosCPData = []
    
    try:
        informacion_contable = InformacionContable_CP.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except ObjectDoesNotExist:
        error = 1

    #Si estadefinida la informacion contable no hay error!!!
    if error == 0:

        if ignorar_documentos_cont:
            documentosCP  = CuentasXPagarDocumento.objects.filter(contabilizado ='N', concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        else:
            documentosCP  = CuentasXPagarDocumento.objects.filter(concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            
        msg, documentosCPData = contabilidad.crear_polizas(
            origen_documentos   = 'cuentas_por_pagar',
            documentos          = documentosCP, 
            depto_co            = depto_co,
            informacion_contable= informacion_contable,
            plantilla           = plantilla,
            crear_polizas_por   = crear_polizas_por,
            crear_polizas_de    = crear_polizas_de,
            msg = msg,
            descripcion = descripcion, 
            connection_name = connection_name,
            usuario_micorsip = usuario_micorsip
        )

    elif error == 1 and msg=='':
        msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

    return documentosCPData, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='cuentas_por_pagar/herramientas/generar_polizas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    documentosData  = []
    msg             = msg_resultados = msg_informacion = ''

    if request.method == 'POST':
        
        form = GenerarPolizasManageForm(request.POST)
        if form.is_valid():
            fecha_ini               = form.cleaned_data['fecha_ini']
            fecha_fin               = form.cleaned_data['fecha_fin']
            ignorar_documentos_cont = form.cleaned_data['ignorar_documentos_cont']
            crear_polizas_por       = form.cleaned_data['crear_polizas_por']
            crear_polizas_de        = form.cleaned_data['crear_polizas_de']
            plantilla               = form.cleaned_data['plantilla']
            descripcion             = form.cleaned_data['descripcion']

            msg = 'es valido'

            documentosData, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_documentos_cont, crear_polizas_por, crear_polizas_de, plantilla, descripcion, connection_name, request.user.username)
            if documentosData == []:
                msg_resultados = 'Lo siento, no se encontraron resultados para este filtro'
            else:
                form = GenerarPolizasManageForm()       
                msg_informacion = 'Polizas generadas satisfactoriamente, *Ahora revisa las polizas pendientes generadas en el modulo de contabilidad'
    else:
        form = GenerarPolizasManageForm()
    c = {'documentos':documentosData,'msg':msg,'form':form, 'msg_resultados':msg_resultados,'msg_informacion':msg_informacion,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##        Preferencias de empresa       ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='cuentas_por_pagar/herramientas/preferencias_empresa.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    try:
        informacion_contable = InformacionContable_CP.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except:
        informacion_contable = InformacionContable_CP()
    condpago = informacion_contable.condicion_pago_contado
    
    form = InformacionContableManageForm(request.POST or None, instance=informacion_contable)
    msg = ''
    if form.is_valid():
        form.save()
        msg = 'Datos Guardados Exitosamente'

    plantillas = PlantillaPolizas_CP.objects.all()
    c= {'form':form,'msg':msg,'plantillas':plantillas,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Plantillas              ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='cuentas_por_pagar/herramientas/plantilla_poliza.html'):
    
    message = ''

    if id:
        plantilla = get_object_or_404(PlantillaPolizas_CP, pk=id)
    else:
        plantilla = PlantillaPolizas_CP()
    
    plantilla_form = PlantillaPolizaManageForm(request.POST or None, instance=plantilla)
    plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
    plantilla_items_formset = plantilla_items(request.POST or None, instance=plantilla)
    
    if plantilla_form.is_valid() and plantilla_items_formset.is_valid():
        plantilla = plantilla_form.save(commit = False)
        plantilla.save()

        #GUARDA CONCEPTOS DE PLANTILLA
        for concepto_form in plantilla_items_formset:
            Detalleplantilla = concepto_form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not Detalleplantilla.id:
                Detalleplantilla.plantilla_poliza_CP = plantilla
        
        plantilla_items_formset.save()
        return HttpResponseRedirect('/cuentas_por_pagar/PreferenciasEmpresa/')
    
    c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_delete(request, id = None):
    plantilla = get_object_or_404(PlantillaPolizas_CP, pk=id)
    plantilla.delete()

    return HttpResponseRedirect('/cuentas_por_pagar/PreferenciasEmpresa/')

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
    tipos_provedores_list = TipoProveedor.objects.all()

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