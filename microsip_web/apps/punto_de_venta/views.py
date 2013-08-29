#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.db import connections, transaction
from django.db.models import Q
# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime, time
from forms import *
from models import *
from microsip_web.apps.main.filtros.models import *
from microsip_web.libs import contabilidad
from triggers import triggers
from microsip_web.apps.main.forms import filtroarticulos_form, filtro_clientes_form

@login_required(login_url='/login/')
def inicializar_tablas(request):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    c = connections[basedatos_activa].cursor()
    #DETALLE DE VENTAS
    c.execute(triggers['SIC_PUNTOS_PV_DOCTOSPVDET_BU'])
    c.execute(triggers['SIC_PUNTOS_PV_DOCTOSPVDET_AD'])
    #VENTAS
    c.execute(triggers['SIC_PUNTOS_PV_DOCTOSPV_BU'])
    c.execute(triggers['SIC_PUNTOS_PV_DOCTOSPV_AD'])
    #CLIENTES
    c.execute(triggers['SIC_PUNTOS_PV_CLIENTES_BU'])
    #EXCEPTION
    try:
        c.execute(
        '''
        CREATE EXCEPTION EX_CLIENTE_SIN_SALDO 'El cliente no tiene suficiente saldo';   
        ''')
    except Exception, e:
       print "Oops!  No pudo agregarse la excepción EX_CLIENTE_SIN_SALDO por que esta ya existe. "

    transaction.commit_unless_managed()
    return HttpResponseRedirect('/punto_de_venta/ventas/')

def create_facturageneral_dia(request, cliente_id=None):
    cliente_id = 331
    # fecha = datetime.date.today()
    # fechahora = datetime.datetime.today()
    # hora = fechahora.time().__str__().split('.')[0]
    # caja = Caja.objects.get(pk=750)
    # detalles = Docto_pv_det.objects.filter(documento_pv__fecha=fecha, documento_pv__cliente__id=cliente_id)
    
    # Docto_PV.objects.create(
    #     id = -1,
    #     caja = caja,
    #     tipo ='F',
    #     folio ='',
    #     fecha = fecha,
    #     hora= hora,
    #     cajero = 

    #     )
    # for detalle in detalles:


    # objects.asdas
    return HttpResponseRedirect('/')


##########################################
##                                      ##
##              Articulos               ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def inicializar_puntos_clientes(request):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    Cliente.objects.update(puntos=0, dinero_electronico=0, hereda_valorpuntos=1, valor_puntos=0)
    TipoCliente.objects.update(valor_puntos=0)
    return HttpResponseRedirect('/punto_de_venta/clientes/')

@login_required(login_url='/login/')
def inicializar_puntos_articulos(request):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    Articulos.objects.update(puntos=0, dinero_electronico=0, hereda_puntos=1)
    LineaArticulos.objects.update(puntos=0, dinero_electronico=0, hereda_puntos=1)
    GrupoLineas.objects.update(puntos=0, dinero_electronico=0)
    
    return HttpResponseRedirect('/punto_de_venta/articulos/')

@login_required(login_url='/login/')
def articulos_view(request, clave='', nombre ='', carpeta=1, template_name='punto_de_venta/articulos/articulos/articulos.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    msg = ''
    if request.method =='POST':
        filtro_form = filtroarticulos_form(request.POST)
        if filtro_form.is_valid():
            articulo = filtro_form.cleaned_data['articulo']
            nombre = filtro_form.cleaned_data['nombre']
            clave = filtro_form.cleaned_data['clave']

            if articulo != None:
                return HttpResponseRedirect('/punto_de_venta/articulo/%s/'% articulo.id)
            elif clave != '':
                clave_articulo = ClavesArticulos.objects.filter(clave=clave)
                if clave_articulo.count() > 0:
                    return HttpResponseRedirect('/punto_de_venta/articulo/%s/'% clave_articulo[0].articulo.id)
                else:
                    articulos_list = Articulos.objects.filter(nombre__icontains=nombre).order_by('nombre')
                    msg='No se encontro ningun articulo con esta clave'
            else:
                articulos_list = Articulos.objects.filter(nombre__icontains=nombre).order_by('nombre')
    else:
        filtro_form = filtroarticulos_form()
        articulos_list = Articulos.objects.filter(Q(carpeta__id=carpeta)| Q(carpeta__id=None)).order_by('nombre') #filter(carpeta = carpeta)
    
    paginator = Paginator(articulos_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        articulos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articulos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articulos = paginator.page(paginator.num_pages)
    
    PATH = request.path
    if  '/ventas/articulos/' in PATH:
        extend = 'ventas/base.html'
    elif '/punto_de_venta/articulos/' in PATH:
        extend = 'punto_de_venta/base.html'

    c = {
        'articulos':articulos,
        'carpeta':carpeta,
        'extend':extend,
        'filtro_form':filtro_form,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def articulo_manageView(request, id = None, template_name='punto_de_venta/articulos/articulos/articulo.html'):
    message = ''

    if id:
        articulo = get_object_or_404(Articulos, pk=id)
    else:
        articulo =  Articulos()
    
    articulos_compatibles = ArticuloCompatibleArticulo.objects.filter(articulo=articulo)
    clasificaciones_compatibles = ArticuloCompatibleCarpeta.objects.filter(articulo=articulo)

    if request.method == 'POST':
        form = ArticuloManageForm(request.POST, instance=  articulo)
        form_articuloCompatible = ArticuloCompatibleArticulo_ManageForm(request.POST)
        #form_clasificacionCompatible = ArticuloCompatibleClasificacion_ManageForm(request.POST)
        
        if form.is_valid():
            articulo = form.save()
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
        form = ArticuloManageForm(instance= articulo)
        form_articuloCompatible = ArticuloCompatibleArticulo_ManageForm()
        #form_clasificacionCompatible = ArticuloCompatibleClasificacion_ManageForm()

    PATH = request.path
    extend='punto_de_venta/base.html'

    if  '/ventas/articulo/' in PATH:
        extend = 'ventas/base.html'
    elif '/punto_de_venta/articulo/' in PATH:
        extend = 'punto_de_venta/base.html'

    c = {
    'form':form,
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
        
# @login_required(login_url='/login/')
# def gruposgrupo_manageView(request, categoria_id=None, template_name='punto_de_venta/articulos/categorias/categoria.html'):
    
#     if request.method == 'POST':
#         grupo_form = GruposGrupo_bypadre_ManageForm(request.POST)

#         if grupo_form.is_valid():
#             newgrupo = grupo_form.cleaned_data['newgrupo']
#             grupo = grupo_form.cleaned_data['grupo']

#             if categoria_id:
#                 grupo_padre = get_object_or_404(GruposGrupo, pk=categoria_id).grupo
#             else:
#                 grupo_padre = None

#             if newgrupo != '':
#                 clasificacionObjeto = Grupo(
#                     nombre = newgrupo,
#                     )
#                 clasificacionObjeto.save()
#             else:
#                 clasificacionObjeto = grupo

#             clasificacion = GruposGrupo(
#                 grupo = clasificacionObjeto,
#                 grupo_padre = grupo_padre,
#                 )

#             clasificacion.save()
            
#             if categoria_id:
#                 return HttpResponseRedirect('/punto_de_venta/articulos/%s'% categoria_id)
#             else:
#                 return HttpResponseRedirect('/punto_de_venta/articulos/')                
#     else:
#         grupo_form = GruposGrupo_bypadre_ManageForm()   

#     c = {'form':grupo_form, }
#     return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##           Clientes                   ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def clientes_view(request, template_name='main/clientes/clientes/clientes.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    msg = ''
    if request.method =='POST':
        filtro_form = filtro_clientes_form(request.POST)
        if filtro_form.is_valid():
            cliente = filtro_form.cleaned_data['cliente']
            nombre = filtro_form.cleaned_data['nombre']
            clave = filtro_form.cleaned_data['clave']

            if cliente != None:
                return HttpResponseRedirect('/punto_de_venta/cliente/%s/'% cliente.id)
            elif clave != '':
                clave_cliente = ClavesClientes.objects.filter(clave=clave)
                if clave_cliente.count() > 0:
                    return HttpResponseRedirect('/punto_de_venta/cliente/%s/'% clave_cliente[0].cliente.id)
                else:
                    clientes_list = Cliente.objects.filter(nombre__icontains=nombre).order_by('nombre')
                    msg='No se encontro ningun cliente con esta clave'
            else:
                clientes_list = Cliente.objects.filter(nombre__icontains=nombre).order_by('nombre')
    else:
        filtro_form = filtro_clientes_form()
        clientes_list = Cliente.objects.all().order_by('nombre')
    
    paginator = Paginator(clientes_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        clientes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        clientes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        clientes = paginator.page(paginator.num_pages)

    c = {'clientes':clientes, 'filtro_form':filtro_form}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def tipos_cliente_view(request, template_name='main/clientes/tipos_cliente/tipos_clientes.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    tipos_cliente_list = TipoCliente.objects.all()

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
        tipo_cliente = get_object_or_404(TipoCliente, pk=id)
    else:
        tipo_cliente =  TipoCliente()
    
    if request.method == 'POST':
        form = TipoClienteManageForm(request.POST, instance=  tipo_cliente)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/punto_de_venta/tipos_cliente/')
    else:
        form = TipoClienteManageForm(instance= tipo_cliente)

    c = {'form':form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def cliente_manageView(request, id = None, template_name='main/clientes/clientes/cliente.html'):
    message = ''

    if id:
        cliente = get_object_or_404(Cliente, pk=id)
    else:
        cliente =  Cliente()
    
    cuentas_ventas = clientes_config_cuenta.objects.all()
    cuentas = {}
    
    for cuenta in cuentas_ventas:
        cuentas[cuenta.campo_cliente]= "Cuenta contable ventas"
        if cuenta.valor_contado_credito != 'Ambos':
            cuentas[cuenta.campo_cliente] += " a %s "% cuenta.valor_contado_credito
        
        if cuenta.valor_iva == 'I':
            cuentas[cuenta.campo_cliente] += " con IVA"
        elif cuenta.valor_iva == '0':
            cuentas[cuenta.campo_cliente] += " sin IVA"

    if request.method == 'POST':
        form = ClienteManageForm(request.POST, instance=  cliente)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/punto_de_venta/clientes/')
    else:
        form = ClienteManageForm(instance= cliente)

    c = {'form':form, 'cuentas':cuentas,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

def cliente_searchView(request, template_name='main/clientes/clientes/cliente_search.html'):
    message = ''
    cliente =  Cliente()
    dinero_en_puntos = 0

    if request.method == 'POST':
        form = ClienteSearchForm(request.POST)
        if form.is_valid():
            try:
                cliente = ClavesClientes.objects.get(clave=form.cleaned_data['cliente']).cliente
                if cliente.hereda_valorpuntos:
                    valor_puntos =  cliente.tipo_cliente.valor_puntos
                else:
                    valor_puntos = cliente.valor_puntos
                        
                dinero_en_puntos =  valor_puntos * cliente.puntos
            except ObjectDoesNotExist:
                cliente = Cliente();
                message='No se encontro un cliente con esta clave, intentalo de nuevo.'
    else:
        form = ClienteSearchForm()
        
    c = {'form':form, 'cliente':cliente,'message':message, 'dinero_en_puntos':dinero_en_puntos, }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##           Lineas articulos           ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def lineas_articulos_view(request, template_name='punto_de_venta/articulos/lineas/lineas_articulos.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    linea_articulos_list = LineaArticulos.objects.all()

    paginator = Paginator(linea_articulos_list, 15) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        lineas_articulos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        lineas_articulos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        lineas_articulos = paginator.page(paginator.num_pages)

    c = {'lineas_articulos':lineas_articulos}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def linea_articulos_manageView(request, id = None, template_name='punto_de_venta/articulos/lineas/linea_articulos.html'):
    message = ''

    if id:
        linea_articulos = get_object_or_404( LineaArticulos, pk=id)
    else:
        linea_articulos =  LineaArticulos()
    
    if request.method == 'POST':
        form = LineaArticulosManageForm(request.POST, instance=  linea_articulos)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/punto_de_venta/lineas_articulos')
    else:
        form = LineaArticulosManageForm(instance= linea_articulos)

    c = {'form':form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##            Grupos lineas             ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def grupos_lineas_view(request, template_name='punto_de_venta/articulos/grupos/grupos_lineas.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    grupos_lineas_list = GrupoLineas.objects.all()

    paginator = Paginator(grupos_lineas_list, 15) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        grupos_lineas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        grupos_lineas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        grupos_lineas = paginator.page(paginator.num_pages)

    c = {'grupos_lineas':grupos_lineas}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def grupo_lineas_manageView(request, id = None, template_name='punto_de_venta/articulos/grupos/grupo_lineas.html'):
    message = ''

    if id:
        grupo_lineas = get_object_or_404( GrupoLineas, pk=id)
    else:
        grupo_lineas =  GrupoLineas()
        
    if request.method == 'POST':
        form = GrupoLineasManageForm(request.POST, instance=  grupo_lineas)
        if form.is_valid():
            grupo = form.save()
            return HttpResponseRedirect('/punto_de_venta/grupos_lineas')
    else:
        form = GrupoLineasManageForm(instance= grupo_lineas)

    c = {'form':form,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##        Generacion de polizas         ##
##                                      ##
##########################################

def generar_polizas(fecha_ini = None, fecha_fin = None, ignorar_documentos_cont = True, crear_polizas_por = 'Documento', crear_polizas_de = '', plantilla_ventas = '', plantilla_devoluciones = '', descripcion = '', basedatos_activa = None, usuario_micorsip=''):
    error   = 0
    msg     = ''
    documentosData = []
    documentosGenerados = []
    documentosDataDevoluciones = []
    depto_co = DeptoCo.objects.get(clave='GRAL')
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
                ventas          = Docto_PV.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D':
                devoluciones        = Docto_PV.objects.filter(estado = 'N').filter(tipo ='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        else:
            if crear_polizas_de     == 'V':
                ventas          = Docto_PV.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
            elif crear_polizas_de   == 'D':
                devoluciones        = Docto_PV.objects.filter(estado = 'N').filter(tipo = 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
        
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
                basedatos_activa =  basedatos_activa,
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
                basedatos_activa = basedatos_activa,
                usuario_micorsip = usuario_micorsip,
            )
            
    elif error == 1 and msg=='':
        msg = 'No se han definido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'
    
    return documentosGenerados, documentosDataDevoluciones, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='punto_de_venta/herramientas/generar_polizas.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    polizas_ventas  = []
    error           = 0
    msg             = msg_informacion =''

    if request.method == 'POST':
        form = GenerarPolizasManageForm( request.POST, database = basedatos_activa )
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
                    basedatos_activa = basedatos_activa,
                    usuario_micorsip = request.user.username,
                    )
            else:
                error =1
                msg = 'Seleciona una plantilla'

            if polizas_ventas == [] and not error == 1:
                msg = 'Lo siento, no se encontraron documentos para ralizar polizas con este filtro'
            elif not polizas_ventas == [] and not error == 1:
                form = GenerarPolizasManageForm( database = basedatos_activa )       
                msg_informacion = 'Polizas generadas satisfactoriamente, *Ahora revisa las polizas pendientes generadas en el modulo de contabilidad'
    else:
        form = GenerarPolizasManageForm( database = basedatos_activa )
    
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
    if request.method == 'POST':
        form = InformacionContableManageForm(request.POST, instance=informacion_contable)
        if form.is_valid():
            form.save()
            msg = 'Datos Guardados Exitosamente'
    else:
        form = InformacionContableManageForm(instance=informacion_contable)

    plantillas = PlantillaPolizas_pv.objects.all()
    c= {'form':form,'msg':msg,'plantillas':plantillas,}
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
    plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
    plantilla_items_formset = plantilla_items(request.POST or None, instance=plantilla)
    
    if plantilla_form.is_valid() and plantilla_items_formset.is_valid():
        plantilla = plantilla_form.save(commit = False)
        plantilla.save()

        #GUARDA CONCEPTOS DE PLANTILLA
        for concepto_form in plantilla_items_formset :
            Detalleplantilla = concepto_form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not Detalleplantilla.id:
                Detalleplantilla.plantilla_poliza_pv = plantilla
        
        plantilla_items_formset .save()
        return HttpResponseRedirect('/punto_de_venta/PreferenciasEmpresa/')
    
    c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##              Ventas                  ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def ventas_de_mostrador_view(request, template_name='punto_de_venta/documentos/ventas/ventas_de_mostrador.html'):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    ventas_list = Docto_PV.objects.filter(tipo='V').order_by('-id')

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
    hay_repetido = False
    if id:
        documento = get_object_or_404(Docto_PV, pk=id)
    else:
        documento = Docto_PV()
    
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
    basedatos_activa =  request.user.userprofile.basedatos_activa
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    documentos_list = Docto_PV.objects.filter(tipo='D')
    
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