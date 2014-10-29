#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import connections, transaction
from django.db.models import Q, Sum, Max
# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime, time
from forms import *
from models import *
from mobi.decorators import detect_mobile
from django.core import management
from microsip_web.apps.main.filtros.models import *
from microsip_web.libs.custom_db.main import next_id
from microsip_web.libs import contabilidad
from microsip_web.apps.main.forms import filtroarticulos_form
from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from microsip_web.libs.punto_de_venta import new_factura_global
from microsip_web.settings.local_settings import MICROSIP_MODULES
##########################################
##                                      ##
##              Articulos               ##
##                                      ##
##########################################
@login_required(login_url='/login/')
def get_precio_articulo(request, template_name='punto_de_venta/articulos/articulos/precio.html'):
    connection_name = get_conecctionname(request.session)
    c = connections[connection_name].cursor()
    articulo = ''
    precio = '' 
    precio_lista= ''
    form = articulo_byclave_form(request.POST or None)
    if form.is_valid():
        clave = form.cleaned_data['clave']
        articulo = ArticuloClave.objects.get(clave=clave).articulo

        c.execute("EXECUTE PROCEDURE GET_PRECIO_ARTCLI(331,%s,'2013/11/27');"%articulo.id)
        row = c.fetchone()
        precio = row[0]
        precio_lista = row[2]
        c.close()

    c = {
        'form':form,
        'articulo':articulo,
        'precio':precio,
        'precio_lista':precio_lista,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def articulo_manageView(request, id = None, template_name='punto_de_venta/articulos/articulos/articulo.html'):
    message = ''

    if id:
        articulo = get_object_or_404(Articulo, pk=id)
    else:
        articulo =  Articulo()
    
    articulos_compatibles = ArticuloCompatibleArticulo.objects.filter(articulo=articulo)
    clasificaciones_compatibles = ArticuloCompatibleCarpeta.objects.filter(articulo=articulo)

    if request.method == 'POST':
        articulo_form = ArticuloManageForm(request.POST, instance=  articulo)
        form_articuloCompatible = ArticuloCompatibleArticulo_ManageForm(request.POST)
        #form_clasificacionCompatible = ArticuloCompatibleClasificacion_ManageForm(request.POST)
        
        if articulo_form.is_valid():
            articulo = articulo_form.save( commit = False )
            articulo.usuario_ult_modif = request.user.username
            articulo.save()

            if 'btnAgregarCompArticulo' in request.POST:
                if form_articuloCompatible.is_valid():
                    articulo_compatible = form_articuloCompatible.cleaned_data['compatible_articulo']
                    articulo_comp = ArticuloCompatibleArticulo(
                        articulo = articulo,
                        articulo_compatible = articulo_compatible,
                        )
                    articulo_comp.save()
                return HttpResponseRedirect('/punto_de_venta/articulo/%s'%id)
            elif 'btnAgregarCompClasificacion' in request.POST:
                if form_clasificacionCompatible.is_valid():
                    clasificacion = form_clasificacionCompatible.save(commit=False)
                    clasificacion.articulo = articulo
                    clasificacion.save()
                return HttpResponseRedirect('/punto_de_venta/articulo/%s'%id)

            return HttpResponseRedirect('/punto_de_venta/articulos/')
    else:
        articulo_form = ArticuloManageForm(instance= articulo)
        form_articuloCompatible = ArticuloCompatibleArticulo_ManageForm()
        #form_clasificacionCompatible = ArticuloCompatibleClasificacion_ManageForm()
        
    extend = 'punto_de_venta/base.html'
    c = {
    'articulo_form':articulo_form,
    'articulos_compatibles':articulos_compatibles,
    'clasificaciones_compatibles':clasificaciones_compatibles,
    'form_articuloCompatible':form_articuloCompatible,
    #'form_clasificacionCompatible':form_clasificacionCompatible,
    'articulo_id':id,
    'extend':extend,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def ArticuloCompatibleArticulo_delete(request, articulo_id=None, articuloCompatibleId= None):
    ArticuloCompatibleArticulo.objects.filter(id=articuloCompatibleId).delete()
    if articulo_id:
        return HttpResponseRedirect('/punto_de_venta/articulo/%s'% articulo_id)

@login_required(login_url='/login/')
def ArticuloCompatibleClasificacion_delete(request, articulo_id=None, articuloCompatibleId= None):
    ArticuloCompatibleCarpeta.objects.filter(id=articuloCompatibleId).delete()
    if articulo_id:
        return HttpResponseRedirect('/punto_de_venta/articulo/%s'% articulo_id)
        
@login_required(login_url='/login/')
def gruposgrupo_delete(request, categoria_padre=None, categoria_id=None, template_name='punto_de_venta/articulos/categorias/categoria.html'):
    GruposGrupo.objects.filter(id=categoria_id).delete()
    if categoria_padre:
        return HttpResponseRedirect('/punto_de_venta/articulos/%s'% categoria_padre)
    else:
        return HttpResponseRedirect('/punto_de_venta/articulos/')
        
##########################################
##                                      ##
##           Clientes                   ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def tipos_cliente_view(request, template_name='main/clientes/tipos_cliente/tipos_clientes.html'):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    tipos_cliente_list = ClienteTipo.objects.all()

    paginator = Paginator(tipos_cliente_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        tipos_cliente = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tipos_cliente = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tipos_cliente = paginator.page(paginator.num_pages)

    c = {'tipos_cliente':tipos_cliente}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def tipo_cliente_manageView(request, id = None, template_name='main/clientes/tipos_cliente/tipo_cliente.html'):
    message = ''

    if id:
        tipo_cliente = get_object_or_404(ClienteTipo, pk=id)
    else:
        tipo_cliente =  ClienteTipo()
    
    if request.method == 'POST':
        form = TipoClienteManageForm(request.POST, instance=  tipo_cliente)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/punto_de_venta/tipos_cliente/')
    else:
        form = TipoClienteManageForm(instance= tipo_cliente)

    c = {'form':form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##        Generacion de polizas         ##
##                                      ##
##########################################

def generar_polizas(fecha_ini = None, fecha_fin = None, ignorar_documentos_cont = True, crear_polizas_por = 'Documento', crear_polizas_de = '', plantilla_ventas = '', plantilla_devoluciones = '', descripcion = '', connection_name = None, usuario_micorsip=''):
    error   = 0
    msg     = ''
    documentosData = []
    documentosGenerados = []
    documentosDataDevoluciones = []
    depto_co = ContabilidadDepartamento.objects.get(clave='GRAL')
    try:
        informacion_contable = InformacionContable_pv.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except ObjectDoesNotExist:
        error = 1
    
    #Si estadefinida la informacion contable no hay error!!!
    if error == 0:

        ventas  = []
        devoluciones= []
        if ignorar_documentos_cont:
            if crear_polizas_de     == 'V':
                ventas          = PuntoVentaDocumento.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D':
                devoluciones        = PuntoVentaDocumento.objects.filter(estado = 'N').filter(tipo ='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        else:
            if crear_polizas_de     == 'V':
                ventas          = PuntoVentaDocumento.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D':
                devoluciones        = PuntoVentaDocumento.objects.filter(estado = 'N').filter(tipo = 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        
        if crear_polizas_de     == 'V':
            msg, documentosData = contabilidad.crear_polizas(
                origen_documentos   = 'punto_de_venta',
                documentos          = ventas, 
                depto_co            = depto_co,
                informacion_contable= informacion_contable,
                plantilla           = plantilla_ventas,
                crear_polizas_por   = crear_polizas_por,
                crear_polizas_de    = crear_polizas_de,
                msg = msg,
                descripcion = descripcion, 
                tipo_documento = 'V',
                connection_name =  connection_name,
                usuario_micorsip = usuario_micorsip,
            )
            documentosGenerados = documentosData
        if crear_polizas_de     == 'D':
            msg, documentosDataDevoluciones = contabilidad.crear_polizas(
                origen_documentos   = 'punto_de_venta',
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
        msg = 'No se han definido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'
    
    return documentosGenerados, documentosDataDevoluciones, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='punto_de_venta/herramientas/generar_polizas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    polizas_ventas  = []
    error           = 0
    msg             = msg_informacion =''

    if request.method == 'POST':
        form = GenerarPolizasManageForm( request.POST)
        if form.is_valid():

            fecha_ini                   = form.cleaned_data['fecha_ini']
            fecha_fin                   = form.cleaned_data['fecha_fin']
            ignorar_documentos_cont     = form.cleaned_data['ignorar_documentos_cont']
            crear_polizas_por           = form.cleaned_data['crear_polizas_por']
            crear_polizas_de            = form.cleaned_data['crear_polizas_de']
            plantilla_ventas            = form.cleaned_data['plantilla_ventas']
            plantilla_devoluciones      = form.cleaned_data['plantilla_devoluciones']
            plantilla_cobros_cc         = form.cleaned_data['plantilla_cobros_cc']
            descripcion                 = form.cleaned_data['descripcion']

            if (crear_polizas_de == 'V' and not plantilla_ventas == None) or (crear_polizas_de == 'D' and not plantilla_devoluciones == None):
                msg = 'es valido'
                polizas_ventas, polizas_devoluciones, msg = generar_polizas(
                    fecha_ini=fecha_ini, 
                    fecha_fin=fecha_fin, 
                    ignorar_documentos_cont=ignorar_documentos_cont, 
                    crear_polizas_por=crear_polizas_por, 
                    crear_polizas_de=crear_polizas_de, 
                    plantilla_ventas=plantilla_ventas, 
                    plantilla_devoluciones=plantilla_devoluciones, 
                    descripcion= descripcion,
                    connection_name = connection_name,
                    usuario_micorsip = request.user.username,
                    )
            else:
                error =1
                msg = 'Seleciona una plantilla'

            if polizas_ventas == [] and not error == 1:
                msg = 'Lo siento, no se encontraron documentos para ralizar polizas con este filtro'
            elif not polizas_ventas == [] and not error == 1:
                form = GenerarPolizasManageForm()       
                msg_informacion = 'Polizas generadas satisfactoriamente, *Ahora revisa las polizas pendientes generadas en el modulo de contabilidad'
    else:
        form = GenerarPolizasManageForm()
    
    c = {'documentos':polizas_ventas,'msg':msg,'form':form,'msg_informacion':msg_informacion,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##        Preferencias de empresa       ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='punto_de_venta/herramientas/preferencias_empresa.html'):
    try:
        informacion_contable = InformacionContable_pv.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except:
        informacion_contable = InformacionContable_pv()


    msg = ''
    general_initialvalues = {
        'articulo_general': Registry.objects.get(nombre='ARTICULO_VENTAS_FG_PV_ID').get_value(),
    }
    preferencias_generalform = PreferenciasGeneralManageForm(request.POST or None, initial= general_initialvalues)

    infcontable_initialvalues = {
        'tipo_poliza_ventas': Registry.objects.get(nombre='TIPO_POLIZA_VENTAS_PV').get_value(),
        'tipo_poliza_devol': Registry.objects.get(nombre='TIPO_POLIZA_DEVOL_PV').get_value(),
        'tipo_poliza_cobros_cc': Registry.objects.get(nombre='TIPO_POLIZA_COBROS_CXC_PV').get_value(),
    }
    form_reg = InformacioncontableRegManageForm( request.POST or None, initial= infcontable_initialvalues)
    form = InformacionContableManageForm(request.POST or None, instance=informacion_contable)
    

    
    fallo = None
    
    if request.POST:
        if form.is_valid():
            form.save()
            msg = 'Datos guardados correctamente'        
        else:
            fallo = True    

        if preferencias_generalform.is_valid():
            preferencias_generalform.save()
            msg = 'Datos guardados correctamente'
        else:
            fallo = True

    if fallo:
        msg = ''
    
    plantillas = PlantillaPolizas_pv.objects.all()
    
    c = {
        'form':form,
        'preferencias_generalform': preferencias_generalform,
        'msg':msg,
        'plantillas':plantillas,
        'form_reg':form_reg, 
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Plantillas              ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='punto_de_venta/herramientas/plantilla_poliza.html'):
    message = ''

    if id:
        plantilla = get_object_or_404(PlantillaPolizas_pv, pk=id)
    else:
        plantilla =PlantillaPolizas_pv()

    plantilla_form = PlantillaPolizaManageForm(request.POST or None, instance=plantilla)
    
    plantilla_items = PlantillaPoliza_items_formset(DetPlantillaPolVentasManageForm, extra=1, can_delete=True)
    plantilla_items_formset = plantilla_items(request.POST or None, instance=plantilla)
    empty_plantilla_form = plantilla_items(None, instance=plantilla)
    
    if plantilla_form.is_valid() and plantilla_items_formset.is_valid():
        plantilla = plantilla_form.save(commit = False)
        plantilla.save()

        #GUARDA CONCEPTOS DE PLANTILLA
        for concepto_form in plantilla_items_formset :
            Detalleplantilla = concepto_form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not Detalleplantilla.id:
                Detalleplantilla.plantilla_poliza_pv = plantilla
                Detalleplantilla.rama =  RamaDetallesPlantilla.objects.get(pk=1)
                Detalleplantilla.tipo_valor = 'Ventas'
                Detalleplantilla.tipo_asiento = 'C'
        
        plantilla_items_formset .save()
        return HttpResponseRedirect('/punto_de_venta/PreferenciasEmpresa/')
    
    c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,'empty_plantilla_form':empty_plantilla_form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Ventas                  ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def ventas_de_mostrador_view(request, template_name='punto_de_venta/documentos/ventas/ventas_de_mostrador.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    ventas_list = PuntoVentaDocumento.objects.filter(tipo='V').order_by('-id')

    paginator = Paginator(ventas_list, 15) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        ventas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ventas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ventas = paginator.page(paginator.num_pages)

    c = {'ventas':ventas}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def venta_mostrador_manageView(request, id = None, template_name='punto_de_venta/documentos/ventas/venta_de_mostrador.html'):
    
    message = ''
    if id:
        documento = get_object_or_404(PuntoVentaDocumento, pk=id)
    else:
        documento = PuntoVentaDocumento()
    
    documento_items = DocumentoPV_items_formset(DocumentoPVDet_ManageForm, extra=1, can_delete=True)
    documentoCobro_items = DocumentoPV_cobro_items_formset(Docto_pv_cobro_ManageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        DocumentoForm = DocumentoPV_ManageForm(request.POST, request.FILES, instance=documento)
        documento_items_formset = documento_items(request.POST, request.FILES, instance=documento)
        documento_cobros_formset = documentoCobro_items(request.POST, request.FILES, instance=documento)
        
        if DocumentoForm.is_valid() and documento_items_formset.is_valid():
            documento = DocumentoForm.save(commit = False)

            documento.cajero = Cajero.objects.filter(usuario='PRUEBA')
            
            #CARGA NUEVO ID
            if not documento.id:
                documento.id = c_get_next_key('ID_DOCTOS')
            
            documento.save()

            #GUARDA ARTICULOS DE Documento
            for articulo_form in documento_items_formset:
                detalle_documento = articulo_form.save(commit = False)
                #PARA CREAR UNO NUEVO
                if not detalle_documento.id:
                    detalle_documento.id = -1
                    detalle_documento.docto_invfis = documento

                documento_items_formset.save()
            return HttpResponseRedirect('/punto_de_venta/ventas/')
    else:
        DocumentoForm= DocumentoPV_ManageForm(instance=documento)
        documento_cobros_formset = documentoCobro_items(instance=documento)
        documento_items_formset = documento_items(instance=documento)
    
    c = {'documentoForm': DocumentoForm, 'formset': documento_items_formset,'cobros_formset':documento_cobros_formset , 'message':message,}

    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Devoluciones            ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def devoluciones_de_ventas_view(request, template_name='punto_de_venta/documentos/devoluciones/devoluciones_de_ventas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    documentos_list = PuntoVentaDocumento.objects.filter(tipo='D')
    
    paginator = Paginator(documentos_list, 15) # Muestra 10 documentos por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        documentos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documentos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documentos = paginator.page(paginator.num_pages)
    
    c = {'documentos':documentos}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Factura                 ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def facturas_view(request, template_name='punto_de_venta/documentos/facturas/facturas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':

        return HttpResponseRedirect('/select_db/')

    facturas_list = PuntoVentaDocumento.objects.filter(tipo='F').order_by('-id')

    paginator = Paginator(facturas_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        facturas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        facturas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        facturas = paginator.page(paginator.num_pages)

    c = {'facturas':facturas,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required( login_url='/login/' )
def factura_manageView( request, id = None, template_name='punto_de_venta/documentos/facturas/factura.html' ):
    message = ''
    connection_name = get_conecctionname(request.session)
    factura_nueva = False
    
    if id:
        factura = get_object_or_404( PuntoVentaDocumento, pk = id )
    else:
        factura = PuntoVentaDocumento()

    #Cargar formularios

    if id:
        factura_form = FacturaManageForm( request.POST or None, instance = factura,)
        factura_items = DocumentoPV_items_formset(DocumentoPVDet_ManageForm, extra=0, can_delete=False)
    else:
        initial_factura = { 'fecha': datetime.now(),}
        factura_form = FacturaManageForm( request.POST or None, instance = factura, initial= initial_factura)
        factura_items = DocumentoPV_items_formset(DocumentoPVDet_ManageForm, extra=1, can_delete=False)
        
    formset = factura_items(request.POST or None, instance=factura)

    factura_global_fm =  factura_global_form(request.POST or None)
   
    if formset.is_valid() and factura_form.is_valid() and factura_global_fm.is_valid():

        factura = factura_form.save(commit=False)

        cliente = factura.cliente
        cliente_clave = first_or_none( ClienteClave.objects.filter( cliente= cliente ) )
        cliente_direccion =  first_or_none( ClienteDireccion.objects.filter( cliente= cliente ) )
        factura_global_tipo = factura_global_fm.cleaned_data['tipo']
        #Si es una factura nueva
        if not factura.id:
            factura_nueva= True
            factura.id= -1
            factura.caja= first_or_none( Caja.objects.all() )
            factura.tipo= 'F'
            factura.aplicado = 'S'
            factura.folio= ''#Se deja vacio para que se calcule el folio al guardar
            factura.fecha= datetime.now()
            factura.hora= datetime.now().strftime('%H:%M:%S')
            factura.clave_cliente= cliente_clave
            factura.cliente= cliente
            factura.clave_cliente_fac= cliente_clave
            factura.cliente_fac= cliente
            factura.direccion_cliente= cliente_direccion
            factura.moneda= Moneda.objects.get(pk= 1)
            factura.impuesto_incluido= 'N'
            factura.tipo_cambio= 1
            factura.unidad_comprom= 'S'
            factura.tipo_descuento= 'I'

            #datos de factura global
            # factura.tipo_gen_fac='R'
            # factura.es_fac_global='S'
            # factura.fecha_ini_fac_global = fecha_ini_fac_global
            # factura.fecha_fin_fac_global = fecha_fin_fac_global

            factura.porcentaje_descuento=0
            
            factura.sistema_origen='PV'
            factura.persona='FACTURA GLOBAL DIARIA'
            factura.usuario_creador= request.user.username
            factura.save()
            

        ventas_en_factura = factura_form.cleaned_data['ventas_en_factura']
        impuestos_venta_neta = factura_form.cleaned_data['impuestos_venta_neta'].split(',')
        impuestos_otros_impuestos = factura_form.cleaned_data['impuestos_otros_impuestos'].split(',')
        impuestos_importe_impuesto = factura_form.cleaned_data['impuestos_importe_impuesto'].split(',')
        impuestos_porcentaje_impuestos = factura_form.cleaned_data['impuestos_porcentaje_impuestos'].split(',')
        impuestos_ids = factura_form.cleaned_data['impuestos_ids'].split(',')

        #Guardar impuestos
        for impuesto_id, venta_neta, otros_impuestos, importe_impuesto, porcentaje_impuesto in zip(impuestos_ids, impuestos_venta_neta, impuestos_otros_impuestos, impuestos_importe_impuesto, impuestos_porcentaje_impuestos ):
            if impuesto_id != "":
                c = connections[connection_name].cursor()
                query =  '''INSERT INTO "IMPUESTOS_DOCTOS_PV" ("DOCTO_PV_ID", "IMPUESTO_ID", "VENTA_NETA", "OTROS_IMPUESTOS", "PCTJE_IMPUESTO", "IMPORTE_IMPUESTO") \
                    VALUES (%s, %s, %s, %s, %s, %s)'''%(factura.id,  impuesto_id, venta_neta,  otros_impuestos, porcentaje_impuesto, importe_impuesto)
                c.execute(query)
                c.close()

        ventas_en_factura_sting = ventas_en_factura
        ventas_faturadas = ventas_en_factura.split(',')

        if ventas_faturadas!= [u'']:
            for venta_facturada in ventas_faturadas:
                venta = PuntoVentaDocumento.objects.get(pk=venta_facturada)
                PuntoVentaDocumentoLiga.objects.create(
                        id = -1,
                        docto_pv_fuente = venta,
                        docto_pv_destino = factura,
                    )
        ventas_ligas = PuntoVentaDocumentoLiga.objects.filter(docto_pv_destino= factura)
        #Se guardan detalles de factura
        for detalle_form in formset:
            detalle = detalle_form.save(commit = False)

            if not detalle.id:
                detalle.id = -1
                detalle.documento_pv = factura
                detalle.unidades_dev = 0
                detalle.precio_unitario_impto = detalle.precio_unitario
                detalle.fpgc_unitario = 0
                detalle.precio_modificado = 'N' 
                detalle.porcentaje_comis = 0 
                detalle.rol = 'N' 
                detalle.notas = 'FOLIOS:'
                detalle.posicion = -1
                detalle.save()

            #Se generan todos los detalles de ligas        
            if factura_global_tipo == 'C' and factura_nueva:
                detalle_ligas = detalle_form.cleaned_data['detalles_liga'].split(',')
                if detalle_ligas!= [u'']:
                    for detalle_liga in detalle_ligas:
                        detalle_doc = PuntoVentaDocumentoDetalle.objects.get(pk=detalle_liga)
                        documento_liga = PuntoVentaDocumentoLiga.objects.get(docto_pv_fuente= detalle_doc.documento_pv)
                        c = connections[connection_name].cursor()
                        query =  '''INSERT INTO "DOCTOS_PV_LIGAS_DET" ("DOCTO_PV_LIGA_ID", "DOCTO_PV_DET_FTE_ID", "DOCTO_PV_DET_DEST_ID") \
                            VALUES (%s, %s, %s)'''%(documento_liga.id, detalle_doc.id , detalle.id)
                        c.execute(query)
                        c.close()

            #Si es una factura global nueva y si es por partida
            if factura_global_tipo == 'P' and factura_nueva:

                #Se generan todos los detalles de ligas
                for docto_pv_liga in ventas_ligas:
                    for detalle_venta in PuntoVentaDocumentoDetalle.objects.filter(documento_pv=docto_pv_liga.docto_pv_fuente):
                        c = connections[connection_name].cursor()
                        query =  '''INSERT INTO "DOCTOS_PV_LIGAS_DET" ("DOCTO_PV_LIGA_ID", "DOCTO_PV_DET_FTE_ID", "DOCTO_PV_DET_DEST_ID") \
                            VALUES (%s, %s, %s)'''%(docto_pv_liga.id, detalle_venta.id, detalle.id)
                        c.execute(query)
                        c.close()
        
        #Para aplicar la factura  
        c = connections[connection_name].cursor()
        query = "EXECUTE PROCEDURE APLICA_FAC_PV(%s,'N');"%factura.id
        c.execute(query)
        c.close()

        transaction.commit_unless_managed()
        management.call_command( 'syncdb', database = connection_name )
        
        message= 'Factura guardada'

    ventas_factura = PuntoVentaDocumentoLiga.objects.filter(docto_pv_destino= factura)

    c = {
        'factura_global_fm':factura_global_fm, 
        'factura_form': factura_form, 
        'formset':formset, 
        'message':message,
        'ventas_factura':ventas_factura, 
        'message':message, 
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))