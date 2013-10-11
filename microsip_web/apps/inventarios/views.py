 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory
from django.forms.models import modelformset_factory

#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.encoding import smart_str, smart_unicode

from django.db import connections, transaction
from django.db.models import Q
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import formset_factory
import datetime, time
import xlrd
from mobi.decorators import detect_mobile
from models import *
from forms import *
from microsip_web.libs.custom_db.main import next_id
from microsip_web.libs.tools import split_seq
from triggers import triggers
from microsip_web.apps.config.models import *
import fdb
from microsip_web.settings.common import MICROSIP_DATABASES, DATABASES
from microsip_web.libs.custom_db.main import get_conecctionname


@login_required(login_url='/login/')
def ArticuloManageView(request, id, template_name='inventarios/articulos/articulo_mobile.html'):
    articulo = get_object_or_404(Articulos, pk=id)

    clavesarticulos_fromset = modelformset_factory(ClavesArticulos, form= claves_articulos_form, can_delete=True,)
    preciosarticulos_fromset = modelformset_factory(PrecioArticulo, form= precios_articulos_form, can_delete=True,)

    impuestos_articulo = ImpuestosArticulo.objects.filter(articulo=articulo)
    if impuestos_articulo.count() > 0:
        impuesto_articulo = impuestos_articulo[0]
    else:
        impuesto_articulo = ImpuestosArticulo()
    
    if request.method == 'POST':
        formset = clavesarticulos_fromset(request.POST, prefix="formset")
        precios_formset = preciosarticulos_fromset(request.POST, prefix="precios_formset")
    else:
        formset = clavesarticulos_fromset(queryset=ClavesArticulos.objects.filter(articulo=articulo), prefix="formset")
        precios_formset = preciosarticulos_fromset(queryset=PrecioArticulo.objects.filter(articulo=articulo), prefix="precios_formset")

    articulo_form = articulos_form(request.POST or None, instance= articulo)
    # precio_articulo_form = precios_articulos_form(request.POST or None, instance=precio_articulo)
    impuesto_articulo_form = impuestos_articulos_form(request.POST or None, instance=impuesto_articulo)

    #Si los datos de los formularios son correctos
    if articulo_form.is_valid()  and impuesto_articulo_form.is_valid() and formset.is_valid(): #and #precios_formset.is_valid()
        articulo_form.save()

        for form in formset :
            clave = form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not clave.id:
                clave.id = -1
                clave.articulo = articulo

        formset.save()

        for form in precios_formset :
            precio = form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not precio.id:
                precio.id = -1
                precio.articulo = articulo

        precios_formset.save()

        impuesto_articulo_form.save()

        return HttpResponseRedirect('/inventarios/articulos/')

    c = {
        'articulo_form':articulo_form,
        'precios_formset':precios_formset,
        'impuesto_articulo_form':impuesto_articulo_form,
        'formset':formset,
    } 
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##               LOGIN                  ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def select_db(request, template_name='main/select_db.html'):
    form = SelectDBForm(request.POST or None, usuario= request.user, conexion_activa = request.session['conexion_activa'])
    message = ''
    conexion_activa = request.session['conexion_activa']
    
    if form.is_valid():
        conexion = form.cleaned_data['conexion'].replace(' ','_')
        request.session['selected_database'] = conexion

        return HttpResponseRedirect('/')
        call_command('runserver')
    else:
        request.session['selected_database'] = ''
    
    c =  {'form':form, 'message':message,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

def ingresar(request):
    message = ''
    formulario = CustomAuthenticationForm(request.POST or None)
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if formulario.is_valid():
        usuario = authenticate(username=request.POST['username'], password=request.POST['password'])
        
        if usuario.is_active:
            login(request, usuario)
            conexion_db = request.POST['conexion_db']
            request.session['conexion_activa'] = ''
            if conexion_db != '':
                request.session['conexion_activa'] = int(conexion_db)

            return HttpResponseRedirect('/select_db/')
        else:
            return render_to_response('noactivo.html', context_instance=RequestContext(request))

    return render_to_response('main/login.html',{'form':formulario, 'message':message,}, context_instance=RequestContext(request))

def logoutUser(request):
    try:
        del request.session['selected_database']
        del request.session['conexion_activa']
    except KeyError:
        pass
    
    logout(request)
    return HttpResponseRedirect('/')

def c_get_next_key(connection_name = None ):
    """ return next value of sequence """
    c = connections[connection_name].cursor()
    c.execute("SELECT GEN_ID( ID_DOCTOS , 1 ) FROM RDB$DATABASE;")
    row = c.fetchone()
    return int(row[0])

##########################################
##                                      ##
##        INVENTARIOS FISICOS           ##
##                                      ##
##########################################

@login_required( login_url = '/login/' )
def invetariofisicolive_manageview( request, template_name = 'inventarios/Inventarios Fisicos/inventario_fisico_live.html' ):
    basedatos_activa = request.session[ 'selected_database' ]
    if basedatos_activa == '':
        return HttpResponseRedirect( '/select_db/' )
    else:
        conexion_activa_id = request.session[ 'conexion_activa' ]
    conexion_name = "%02d-%s"%( conexion_activa_id, basedatos_activa )

    salida = DoctosIn.objects.get(folio='000000001', concepto = 38)
    entrada = DoctosIn.objects.get(folio='000000002', concepto = 27)

    detalles_inv = DoctosInDet.objects.filter( Q( doctosIn = entrada ) | Q( doctosIn = salida ) )
    form = DoctoInDetManageForm( request.POST or None )
    

    if form.is_valid():
        detalle = form.save( commit = False )

        detalle.id = next_id( 'ID_DOCTOS', conexion_name )
        if detalle.unidades > 0:
            detalle.doctosIn = entrada
            detalle.almacen = entrada.almacen
            detalle.concepto = entrada.concepto
            detalle.tipo_movto ='E'
        elif detalle.unidades < 0:
            detalle.doctosIn = salida
            detalle.almacen = salida.almacen
            detalle.concepto = salida.concepto
            detalle.unidades = detalle.unidades * -1
            detalle.tipo_movto ='S'
        detalle.costo_total = detalle.unidades * detalle.costo_unitario
        det_id=  detalle.id
        detalle.save()

        # c = connections[ conexion_name ].cursor()
        # c.execute("EXECUTE PROCEDURE APLICA_DOCTO_IN %s;"% detalle.id)
        # transaction.commit_unless_managed()
        # c.close()
        # if detalle.tipo_movto == 'E':
        #     c.execute('EXECUTE PROCEDURE APLICA_DOCTO_IN (%s)'% entrada.id)
        # elif detalle.tipo_movto == 'S':
        #     c.execute('EXECUTE PROCEDURE APLICA_DOCTO_IN (%s)'% salida.id)



    c = { 'detalles_inv' : detalles_inv, 'form' : form, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@detect_mobile
@login_required( login_url = '/login/' )
def invetariosfisicos_view( request, template_name = 'inventarios/Inventarios Fisicos/inventarios_fisicos.html' ):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )
    
    inventarios_fisicos = DoctosInvfis.objects.filter(aplicado='N', cancelado='N').order_by('-fecha')

    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False
       
    if request.mobile:
        url_inventario = '/inventarios/inventarioFisico_mobile/'
    else:
        url_inventario = '/inventarios/inventariofisico/'

    c = { 'inventarios_fisicos' : inventarios_fisicos, 'url_inventario' : url_inventario, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

def inventario_getnew_folio():
    registro_folioinventario = Registry.objects.get( nombre = 'SIG_FOLIO_INVFIS' )
    folio = registro_folioinventario.valor 
    siguiente_folio = "%09d" % ( int( folio ) +1 )
    registro_folioinventario.valor = siguiente_folio
    registro_folioinventario.save()
    return folio

@login_required(login_url='/login/')
def create_invetarioFisico_createView( request, template_name = 'inventarios/Inventarios Fisicos/create_inventario_fisico.html' ):
    message = ''
    connection_name = get_conecctionname( request.session )
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )

    form = DoctoInvfis_CreateForm( request.POST or None )
    
    ultimofolio = Registry.objects.filter( nombre = 'SIG_FOLIO_INVFIS' )

    if not ultimofolio.exists():
        message = 'Para poder crear un inventario es nesesario Asignarles folios automaticos a estos'
    else:
        if form.is_valid():
            folio = inventario_getnew_folio()
            inventario = form.save( commit = False )
            inventario.id = -1
            inventario.folio = folio
            inventario.usuario_creador = request.user.username
            inventario.usuario_aut_creacion = request.user.username
            inventario.usuario_ult_modif = request.user.username
            inventario.usuario_aut_modif = request.user.username
            inventario.save()
            return HttpResponseRedirect( '/inventarios/inventariosfisicos/' )
        
    c = { 'message' : message,'form' : form }
    return render_to_response( template_name, c, context_instance=RequestContext( request ) )

@detect_mobile
@login_required( login_url = '/login/' )
def invetarioFisico_manageView( request, id = None, dua = '1', template_name = 'inventarios/Inventarios Fisicos/inventario_fisico.html' ):
    basedatos_activa = request.session[ 'selected_database' ]
    if basedatos_activa == '':
        return HttpResponseRedirect( '/select_db/' )
    else:
        conexion_activa_id = request.session[ 'conexion_activa' ]
    conexion_name = "%02d-%s"%( conexion_activa_id, basedatos_activa )

    message = ''
    msg_series=''
    error = 0
    inicio_form = False
    movimiento = ''
    InventarioFisico = DoctosInvfis.objects.get( pk = id )    
    
    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False

    if request.mobile:
        detallesInventario = []
    else:
        if dua == '1':
            detallesInventario = DoctosInvfisDet.objects.filter( docto_invfis = InventarioFisico ).filter( Q( usuario_ult_modif = request.user.username ) | Q( usuario_ult_modif = None ) ).order_by( '-fechahora_ult_modif' )
        else:
            detallesInventario = DoctosInvfisDet.objects.filter( docto_invfis = InventarioFisico ).order_by( '-fechahora_ult_modif' )

    articulos_discretos_formset = formset_factory( ArticulosDiscretos_ManageForm )
    articulos_discretos_actuales = []
    #POST
    if request.method == 'POST':
        detalleInvForm = DoctosInvfisDetManageForm( request.POST )
        ubicacion_form = UbicacionArticulosForm( request.POST )
        if detalleInvForm.is_valid():
            articulos_discretos_formset = articulos_discretos_formset( request.POST, request.FILES )
            detalleInv = detalleInvForm.save( commit = False )  
            unidades = abs( detalleInv.unidades )
            total_forms = abs( articulos_discretos_formset.total_form_count() )
            if detalleInv.articulo.seguimiento == 'L':
                message = 'La aplicacion no esta preparada para trabajar con articulos de lotes, porfavor introduce estos articulos directamente en microsip'
                error = 1
            
            #Para cargar por primera ves el formset de los numeros de serie del articulo
            if detalleInv.articulo.seguimiento == 'S':
                if detalleInv != '':
                    doc_det = DoctosInvfisDet.objects.filter( docto_invfis = InventarioFisico, articulo = detalleInv.articulo )
                    if doc_det.count() > 0:
                        articulos_discretos_actuales = DesgloseEnDiscretosInvfis.objects.filter(
                        docto_invfis_det = doc_det[0].id )

                if total_forms != unidades:
                    inicio_form = True
                    data = request.POST
                    data['form-TOTAL_FORMS']= str(unidades)
                    for numero in range(unidades):
                        data['form-%s-articulo'% numero]= str(detalleInv.articulo.id)
                        data['form-%s-clave'% numero]= ''

                    articulos_discretos_formset = formset_factory(ArticulosDiscretos_ManageForm)
                    articulos_discretos_formset = articulos_discretos_formset(data)

            else:
                articulos_discretos_formset = formset_factory(ArticulosDiscretos_ManageForm)
                data = {
                    'form-TOTAL_FORMS': u'0',
                    'form-INITIAL_FORMS': u'0',
                    'form-MAX_NUM_FORMS': u'',
                }
                articulos_discretos_formset = articulos_discretos_formset(data)

            if total_forms == unidades or detalleInv.articulo.seguimiento == 'N':
                if articulos_discretos_formset.is_valid()  and ubicacion_form.is_valid() and (articulos_discretos_formset.total_form_count() > 0 or detalleInv.articulo.seguimiento == 'N'):
                    unidades = 0
                    try:
                        doc = DoctosInvfisDet.objects.get(docto_invfis=InventarioFisico, articulo=detalleInv.articulo)
                        id_detalle = doc.id
                        
                        unidades = doc.unidades + detalleInv.unidades
                        
                        if unidades < 0:
                            unidades = 0

                        movimiento = 'actualizar'

                    except ObjectDoesNotExist:
                        if detalleInv.unidades >= 0:
                            id_detalle = c_get_next_key( conexion_name)
                            detalleInv.id = id_detalle
                            articulos_claves =ClavesArticulos.objects.filter( articulo = detalleInv.articulo )
                            
                            if articulos_claves.count() < 1:
                                articulo_clave = ''
                            else:
                                articulo_clave = articulos_claves[0].clave

                            detalleInv.clave = articulo_clave
                            detalleInv.docto_invfis = InventarioFisico
                            movimiento = 'crear'
                    
                    if detalleInv.articulo.seguimiento == 'S':    
                        for form in articulos_discretos_formset.forms:
                            form = form.save( commit = False )
                            art_discreto = ArticulosDiscretos.objects.filter( articulo = form.articulo, clave = form.clave )

                            if art_discreto.count() > 0:
                                art_discreto = art_discreto[0]
                            else:
                                art_discreto = ArticulosDiscretos.objects.create( id = next_id( 'ID_CATALOGOS', conexion_name ), clave = form.clave, articulo = form.articulo, tipo ='S', fecha = None )        

                            if DesgloseEnDiscretosInvfis.objects.filter( art_discreto = art_discreto ).exists() and detalleInv.unidades > 0:
                                msg_series = 'Ya existe un articulo registrado en inventario con numero de serie [%s]'%form.clave
                                error = 1                                
                            if error == 0:
                                if detalleInv.unidades > 0 :
                                    if movimiento == 'crear':
                                        detalleInv.save()

                                    DesgloseEnDiscretosInvfis.objects.create(
                                        id = -1, 
                                        docto_invfis_det = DoctosInvfisDet.objects.get( id = id_detalle ),
                                        art_discreto = art_discreto,
                                        unidades = 1,
                                        sic_nuevo = 'S',
                                        )
                                else:
                                    desgloses_a_eliminar = DesgloseEnDiscretosInvfis.objects.filter( art_discreto = art_discreto )
                                    
                                    if desgloses_a_eliminar.count() <= 0:
                                        error = 2
                                        msg_series = 'No extiste registrado un articulo con este numero de serie en el inventario, no se eliminara'
                                    else:
                                        desgloses_a_eliminar.delete()
                    if error == 0:
                        if movimiento == 'crear':
                            detalleInv.usuario_ult_modif = request.user.username
                            detalleInv.detalle_modificaciones = '[%s/%s=%s], '%( request.user.username, ubicacion_form.cleaned_data[ 'ubicacion' ], detalleInvForm.cleaned_data[ 'unidades' ] )
                            detalleInv.detalle_modificacionestime = '[%s/%s=%s](%s),'%( request.user.username, ubicacion_form.cleaned_data[ 'ubicacion' ], detalleInvForm.cleaned_data[ 'unidades' ], datetime.now().strftime("%d-%m-%Y %H:%M") )
                            # c = connections[conexion_name].cursor()
                            
                            # fecha_actual_str = datetime.now().strftime("%m/%d/%Y")
                            # fecha_inventario_str = InventarioFisico.fecha.strftime("%m/01/%Y")

                            # c.execute("""
                            #     SELECT B.inv_fin_unid FROM orsp_in_aux_art( %s, '%s', '%s','%s','S','N') B
                            #     """% (detalleInv.articulo.id , InventarioFisico.almacen.nombre, fecha_inventario_str, fecha_actual_str))
                            # unidades_rows = c.fetchall()
                            # unidades_mov = unidades_rows[0][0]
                            # c.close() 
                            # detalleInv.unidades_syn = 0
                            # if unidades_mov < 0:
                            #     detalleInv.unidades_syn = unidades_mov

                            detalleInv.save()
                        elif movimiento == 'actualizar':
                            detalleInv = DoctosInvfisDet.objects.get( id = id_detalle )
                            detalleInv.fechahora_ult_modif = datetime.now()
                            detalleInv.unidades = unidades
                            detalleInv.usuario_ult_modif = request.user.username
                            if detalleInv.detalle_modificaciones == None:
                                detalleInv.detalle_modificaciones = ''
                            nuevo_texto = detalleInv.detalle_modificaciones + '[%s/%s=%s],'%( request.user.username, ubicacion_form.cleaned_data[ 'ubicacion' ], detalleInvForm.cleaned_data[ 'unidades' ] )
                            tamano_detalles = len( nuevo_texto )
                            
                            if tamano_detalles < 400:
                                detalleInv.detalle_modificaciones = nuevo_texto
                            else:
                                message = "El numero de caracteres para detalles del articulo fue excedido"
                            detalleInv.detalle_modificacionestime += '[%s/%s=%s](%s),'%( request.user.username, ubicacion_form.cleaned_data[ 'ubicacion' ], detalleInvForm.cleaned_data[ 'unidades' ], datetime.now().strftime("%d-%m-%Y %H:%M") )
                            detalleInv.save()

                        return HttpResponseRedirect('/inventarios/inventariofisico/%s/%s/'% (id, dua))
                           
    else:
        detalleInvForm = DoctosInvfisDetManageForm()
        ubicacion_form = UbicacionArticulosForm()

        articulos_discretos_formset = formset_factory( ArticulosDiscretos_ManageForm )
        data = {
            'form-TOTAL_FORMS': u'0',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
        articulos_discretos_formset = articulos_discretos_formset( data )
    if request.mobile:
        articulos_eninventario = 0
    else:
        articulos_eninventario = detallesInventario.count()
    paginator = Paginator( detallesInventario, 30 ) # Muestra 5 inventarios por pagina
    page = request.GET.get( 'page' )

    #####PARA PAGINACION##############
    try:
        detallesInventario = paginator.page( page )
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        detallesInventario = paginator.page( 1 )
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        detallesInventario = paginator.page( paginator.num_pages )

    lineas_form = linea_articulos_form()

    c = {
        'message' : message,
        'lineas_form' : lineas_form,
        'inicio_form' : inicio_form, 
        'msg_series' : msg_series, 
        'detallesInventario' : detallesInventario,
        'detalleInvForm' : detalleInvForm, 
        'InventarioFisico' : InventarioFisico,
        'ubicacion_form' : ubicacion_form,
        'formset' : articulos_discretos_formset,
        'inventario_id' : id,
        'articulos_eninventario' : articulos_eninventario,
        'articulos_discretos_actuales' : articulos_discretos_actuales,
        }

    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required( login_url = '/login/' )
def invetarioFisico_delete( request, id = None ):
    inventario_fisico = get_object_or_404(DoctosInvfis, pk=id)
    inventario_fisico.delete()

    return HttpResponseRedirect( '/invenatrios/InventariosFisicos/' )


### INVENTARIO FISICO MOBILE

@login_required( login_url = '/login/' )
def invetarioFisico_mobile_pa_manageView( request, id, template_name = 'inventarios/Inventarios Fisicos/inventario_fisico_mobile.html' ):
    InventarioFisico = DoctosInvfis.objects.get( pk = id )
    detalleInvForm = DoctosInvfisDetManageForm()

    c = { 'detalleInvForm' : detalleInvForm, 'InventarioFisico' : InventarioFisico, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )    

def invetarioFisico_mobile_series_manageView( request, id, no_series, template_name = 'inventarios/Inventarios Fisicos/inventario_fisico_mobile_ns.html' ):
    doc_det = DoctosInvfisDet.objects.filter( docto_invfis__id = 21270, articulo__id = id )
    
    if doc_det.count() > 0:
        articulos_discretos_actuales = DesgloseEnDiscretosInvfis.objects.filter(
        docto_invfis_det = doc_det[0].id )

    articulos_discretos_formset = formset_factory( ArticulosDiscretos_ManageForm, extra = int( no_series ) )
    
    articulos_discretos_formset = articulos_discretos_formset()

    c = { 'articulos_discretos_actuales' : articulos_discretos_actuales, 'formset' : articulos_discretos_formset, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )    

##########################################
##                                      ##
##                ENTRADAS              ##
##                                      ##
##########################################

@login_required( login_url = '/login/' )
def entradas_View( request, template_name = 'inventarios/Entradas/entradas.html' ):
    entradas_list = DoctosIn.objects.filter( naturaleza_concepto = 'E' ).order_by( '-fecha' ) 

    paginator = Paginator( entradas_list, 15 ) # Muestra 5 inventarios por pagina
    page = request.GET.get( 'page' )

    #####PARA PAGINACION##############
    try:
        entradas = paginator.page( page )
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entradas = paginator.page( 1 )
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entradas = paginator.page( paginator.num_pages )

    c = { 'entradas' : entradas }
    return render_to_response( template_name, c, context_instance=RequestContext( request ) )

@login_required( login_url='/login/' )
def entrada_manageView( request, id = None, template_name='inventarios/Entradas/entrada.html' ):
    message = ''
    hay_repetido = False
    if id:
        Entrada = get_object_or_404( DoctosIn, pk = id )
    else:
        Entrada = DoctosIn()

    if request.method == 'POST':
        Entrada_form = DoctosInManageForm( request.POST, request.FILES, instance = Entrada )

        #PARA CARGAR DATOS DE EXCEL
        if 'excel' in request.POST:
            input_excel = request.FILES[ 'file_inventario' ]
            book = xlrd.open_workbook( file_contents = input_excel.read() )
            sheet = book.sheet_by_index( 0 )
            articulos = Articulos.objects.filter( es_almacenable = 'S' )

            Entrada_items = doctoIn_items_formset( DoctosInDetManageForm, extra = articulos.count(), can_delete = True )
            
            lista = []
            lista_articulos = []        

            for i in range(sheet.nrows):
                clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
                if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
                    if clave_articulo.articulo.id in lista_articulos:
                        message = 'El Articulo [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% clave_articulo.articulo.nombre
                        hay_repetido = True
                    lista.append({'articulo': clave_articulo.articulo, 'clave':clave_articulo.clave, 'unidades':int(sheet.cell_value(i,1)),})
                    lista_articulos.append(clave_articulo.articulo.id)

            
            articulos_enceros = Articulos.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
            
            for i in articulos_enceros:
                
                #clave_articulo = ClavesArticulos.objects.filter(articulo__id=i.id)
                articulosclav = ClavesArticulos.objects.filter(articulo__id=i.id)
                if articulosclav:
                    lista.append({'articulo': i, 'clave':articulosclav[0].clave , 'unidades':0,})   
                else:
                    lista.append({'articulo': i, 'clave':'', 'unidades':0,})    

            EntradaItems_formset = Entrada_items(initial=lista)
        #GUARDA CAMBIOS EN INVENTARIO FISICO
        else:
            Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
            EntradaItems_formset = Entrada_items(request.POST, request.FILES, instance=Entrada)
            
            if Entrada_form.is_valid() and EntradaItems_formset.is_valid():
                Entrada = Entrada_form.save(commit = False)

                #CARGA NUEVO ID
                if not Entrada.id:
                    Entrada.id = c_get_next_key('ID_DOCTOS')
                    Entrada.naturaleza_concepto = 'E'
                
                Entrada.save()

                #GUARDA ARTICULOS DE INVENTARIO FISICO
                for articulo_form in EntradaItems_formset:
                    DetalleEntrada = articulo_form.save(commit = False)
                    #PARA CREAR UNO NUEVO
                    if not DetalleEntrada.id:
                        DetalleEntrada.id = -1
                        DetalleEntrada.almacen = Entrada.almacen
                        DetalleEntrada.concepto = Entrada.concepto
                        DetalleEntrada.docto_invfis = Entrada
                
                EntradaItems_formset.save()
                return HttpResponseRedirect('/Entradas/')
    else:
        Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
        Entrada_form= DoctosInManageForm(instance=Entrada)
        EntradaItems_formset = Entrada_items(instance=Entrada)
    
    c = {'Entrada_form': Entrada_form, 'formset': EntradaItems_formset, 'message':message,}

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def entrada_delete(request, id = None):
    entrada = get_object_or_404(DoctosIn, pk=id)
    entrada.delete()

    return HttpResponseRedirect('/Entradas/')

##########################################
##                                      ##
##                SALIDAS               ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def salidas_View(request, template_name='inventarios/Salidas/salidas.html'):
    salidas_list = DoctosIn.objects.filter(naturaleza_concepto='S').order_by('-fecha') 

    paginator = Paginator(salidas_list, 15) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        salidas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        salidas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        salidas = paginator.page(paginator.num_pages)

    c = {'salidas':salidas}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def salida_manageView(request, id = None, template_name='inventarios/Salidas/salida.html'):
    message = ''
    hay_repetido = False
    if id:
        Salida = get_object_or_404(DoctosIn, pk=id)
    else:
        Salida = DoctosIn()

    if request.method == 'POST':
        Salida_form = DoctosInManageForm(request.POST, request.FILES, instance=Salida)

        #PARA CARGAR DATOS DE EXCEL
        if 'excel' in request.POST:
            input_excel = request.FILES['file_inventario']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)
            articulos = Articulos.objects.filter(es_almacenable='S')

            Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=articulos.count(), can_delete=True)
            
            lista = []
            lista_articulos = []        

            for i in range(sheet.nrows):
                clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
                if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
                    if clave_articulo.articulo.id in lista_articulos:
                        message = 'El Articulo [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% clave_articulo.articulo.nombre
                        hay_repetido = True
                    lista.append({'articulo': clave_articulo.articulo, 'clave':clave_articulo.clave, 'unidades':int(sheet.cell_value(i,1)),})
                    lista_articulos.append(clave_articulo.articulo.id)

            
            articulos_enceros = Articulos.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
            
            for i in articulos_enceros:
                
                #clave_articulo = ClavesArticulos.objects.filter(articulo__id=i.id)
                articulosclav = ClavesArticulos.objects.filter(articulo__id=i.id)
                if articulosclav:
                    lista.append({'articulo': i, 'clave':articulosclav[0].clave , 'unidades':0,})   
                else:
                    lista.append({'articulo': i, 'clave':'', 'unidades':0,})    

            SalidaItems_formset = Salida_items(initial=lista)
        #GUARDA CAMBIOS EN INVENTARIO FISICO
        else:
            Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
            SalidaItems_formset = Salida_items(request.POST, request.FILES, instance=Salida)
            
            if Salida_form.is_valid() and SalidaItems_formset.is_valid():
                Salida = Salida_form.save(commit = False)

                #CARGA NUEVO ID
                if not Salida.id:
                    Salida.id = c_get_next_key('ID_DOCTOS')
                
                Salida.save()

                #GUARDA ARTICULOS DE INVENTARIO FISICO
                for articulo_form in SalidaItems_formset:
                    DetalleSalida = articulo_form.save(commit = False)
                    #PARA CREAR UNO NUEVO
                    if not DetalleSalida.id:
                        DetalleSalida.id = -1
                        DetalleSalida.almacen = Salida.almacen
                        DetalleSalida.concepto = Salida.concepto
                        DetalleSalida.docto_invfis = Salida
                
                SalidaItems_formset.save()
                return HttpResponseRedirect('/Salidas/')
    else:
        Salida_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)
        Salida_form= DoctosInManageForm(instance=Salida)
        SalidaItems_formset = Salida_items(instance=Salida)
    
    c = {'Salida_form': Salida_form, 'formset': SalidaItems_formset, 'message':message,}

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def salida_delete(request, id = None):
    salida = get_object_or_404(DoctosIn, pk=id)
    salida.delete()

    return HttpResponseRedirect('/Salidas/')

