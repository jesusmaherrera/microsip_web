#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from models import *
from forms import *
from django.db.models import Sum, Max
# user autentication
from django.contrib.auth.decorators import login_required, permission_required

def generar_polizas(fecha_ini = None, fecha_fin = None, ignorar_documentos_cont = True, crear_polizas_por = 'Documento', crear_polizas_de = '', plantilla_facturas = '', plantilla_devoluciones ='', descripcion = '', connection_name = None, usuario_micorsip=''):
    error   = 0
    msg     = ''
    documentosData = []
    documentosGenerados = []
    documentosDataDevoluciones = []
    depto_co = ContabilidadDepartamento.objects.get(clave='GRAL')
    try:
        informacion_contable = InformacionContable_V.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except ObjectDoesNotExist:
        error = 1
    
    #Si estadefinida la informacion contable no hay error!!!
    if error == 0:

        facturas    = []
        devoluciones= []
        if ignorar_documentos_cont:
            if crear_polizas_de     == 'F' or crear_polizas_de  == 'FD':
                facturas            = VentasDocumento.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D' or crear_polizas_de  == 'FD':
                devoluciones        = VentasDocumento.objects.filter(estado = 'N').filter(tipo  ='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        else:
            if crear_polizas_de     == 'F' or crear_polizas_de  == 'FD':
                facturas            = VentasDocumento.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D' or crear_polizas_de  == 'FD':
                devoluciones        = VentasDocumento.objects.filter(estado = 'N').filter(tipo  = 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

        #PREFIJO
        prefijo = informacion_contable.tipo_poliza_ve.prefijo
        if not informacion_contable.tipo_poliza_ve.prefijo:
            prefijo = ''

        if crear_polizas_de     == 'F' or crear_polizas_de  == 'FD':
            msg, documentosData = contabilidad.crear_polizas(
                origen_documentos   = 'ventas',
                documentos          = facturas, 
                depto_co            = depto_co,
                informacion_contable= informacion_contable,
                plantilla           = plantilla_facturas,
                crear_polizas_por   = crear_polizas_por,
                crear_polizas_de    = crear_polizas_de,
                msg = msg,
                descripcion = descripcion, 
                tipo_documento = 'F',
                connection_name = connection_name,
                usuario_micorsip = usuario_micorsip,
            )
            documentosGenerados = documentosData
        if crear_polizas_de     == 'D' or crear_polizas_de  == 'FD':
            msg, documentosDataDevoluciones = contabilidad.crear_polizas(
                origen_documentos   = 'ventas',
                documentos          = devoluciones, 
                depto_co            = depto_co,
                informacion_contable= informacion_contable,
                plantilla           = plantilla_devoluciones,
                crear_polizas_por   = crear_polizas_por,
                crear_polizas_de    = crear_polizas_de,
                msg = msg,
                descripcion = descripcion, 
                tipo_documento = 'D',
                connection_name = connection_name,
                usuario_micorsip = usuario_micorsip,
            )

    elif error == 1 and msg=='':
        msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'
    
    return documentosGenerados, documentosDataDevoluciones, msg

@login_required(login_url='/login/')
def facturas_View(request, template_name='ventas/herramientas/generar_polizas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    documentosData = []
    polizas_de_devoluciones = []
    msg             = msg_informacion =''
    error = 0

    if request.method == 'POST':
        form = GenerarPolizasManageForm(request.POST)
        if form.is_valid():

            fecha_ini               = form.cleaned_data['fecha_ini']
            fecha_fin               = form.cleaned_data['fecha_fin']
            ignorar_documentos_cont = form.cleaned_data['ignorar_documentos_cont']
            crear_polizas_por       = form.cleaned_data['crear_polizas_por']
            crear_polizas_de        = form.cleaned_data['crear_polizas_de']
            plantilla_facturas      = form.cleaned_data['plantilla']
            plantilla_devoluciones  = form.cleaned_data['plantilla_2']
            descripcion             = form.cleaned_data['descripcion']
            if (crear_polizas_de == 'F' and not plantilla_facturas== None) or (crear_polizas_de == 'D' and not plantilla_devoluciones== None) or (crear_polizas_de == 'FD' and not plantilla_facturas== None and not plantilla_devoluciones== None):
                documentosData, polizas_de_devoluciones, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_documentos_cont, crear_polizas_por, crear_polizas_de, plantilla_facturas, plantilla_devoluciones, descripcion, connection_name, request.user.username)
            else:
                error =1
                msg = 'Seleciona una plantilla'

            if (crear_polizas_de == 'F' or crear_polizas_de=='FD') and documentosData == [] and msg=='':
                msg = 'Lo siento, no se encontraron facturas para este filtro'
            elif (crear_polizas_de == 'D' or crear_polizas_de=='FD') and polizas_de_devoluciones == [] and msg=='':
                msg = 'Lo siento, no se encontraron devoluciones para este filtro'
            
            if crear_polizas_de == 'FD' and documentosData == [] and polizas_de_devoluciones == []:
                msg = 'Lo siento, no se encontraron facturas ni devoluciones para este filtro'
            
            if (not documentosData == [] or not polizas_de_devoluciones == []) and error == 0:
                form = GenerarPolizasManageForm()       
                msg_informacion = 'Polizas generadas satisfactoriamente, *Ahora revisa las polizas pendientes generadas en el modulo de contabilidad'
    else:
        form = GenerarPolizasManageForm()
    
    c = {'documentos':documentosData, 'polizas_de_devoluciones':polizas_de_devoluciones,'msg':msg,'form':form,'msg_informacion':msg_informacion,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))