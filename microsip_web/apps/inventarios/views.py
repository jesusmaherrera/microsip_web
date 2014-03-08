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
from django.core import management
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.encoding import smart_str, smart_unicode
from microsip_web.libs.custom_db.procedures import procedures
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
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, runsql_rows, get_conecctionname, first_or_none
from microsip_web.libs.inventarios import ajustes_get_or_create

from microsip_web.settings.local_settings import MICROSIP_MODULES

from microsip_web.libs.tools import split_seq
from triggers import triggers
from microsip_web.apps.config.models import *
import fdb
from microsip_web.settings.common import MICROSIP_DATABASES, DATABASES
from django.db.models import Sum
from microsip_web.apps.config.models import DerechoUsuario

def abrir_inventario_byalmacen(request, almacen_id, template_name = 'inventarios/almacenes/abrir_inventario.html'):
    almacen = Almacen.objects.get( pk = almacen_id )
    almacenform = almacen_inventariando_form(request.POST or None, instance=  almacen)
    
    if almacenform.is_valid():
        almacen_form = almacenform.save(commit= False)
        almacen_form.inventariando = True
        almacen_form.save(update_fields=['inventariando','inventario_conajustes', 'inventario_modifcostos',])
        
        return HttpResponseRedirect( '/inventarios/almacenes/' )
    c = { 'form': almacenform, 'almacen_nombre': almacen.nombre, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@detect_mobile
@login_required( login_url = '/login/' )
def almacenes_view( request, template_name = 'inventarios/almacenes/almacenes.html' ):
    ''' Muestra almacenes con link para entrar a hacer inventario en cada uno de ellos  '''

    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )
    
    almacenes = Almacen.objects.all()

    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False
       
    if request.mobile:
        url_inventario = '/inventarios/inventariofisicomobile/'
    else:
        url_inventario = '/inventarios/inventariofisico/'

    c = { 'almacenes': almacenes, 'url_inventario': url_inventario, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required(login_url='/login/')
def ArticuloManageView(request, id, template_name='inventarios/articulos/articulo.html'):
    ''' Modificacion de datos de un articulo '''

    articulo = get_object_or_404(Articulo, pk=id)

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

    #Si los datos de los formularios son correctos # and 
    if articulo_form.is_valid() and formset.is_valid() and impuesto_articulo_form.is_valid() and precios_formset.is_valid():
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

        impuesto_articulo_form.save(commit = False)
        if not impuesto_articulo.id:
            impuesto_articulo.id = -1
        impuesto_articulo.articulo = articulo
        impuesto_articulo.save()

        return HttpResponseRedirect('/inventarios/articulos/')

    extend = 'inventarios/base.html'

    c = {
        'articulo_form':articulo_form,
        'precios_formset':precios_formset,
        'impuesto_articulo_form':impuesto_articulo_form,
        'formset':formset,
        'extend':extend,
    } 
    return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
##                                      ##
##               LOGIN                  ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def select_db(request, template_name='main/select_db.html'):
    ''' Para seleccionar base de datos con la que se desea trabjar '''

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
    ''' logea un usuario '''

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
    ''' Deslogea un usuario '''
    
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

def allow_microsipuser( username = None, clave_objeto=  None ):
    ''' Checa si el usuario indicado tiene el pribilegio indicado '''

    return DerechoUsuario.objects.filter(usuario__nombre = username, clave_objeto = clave_objeto).exists() or username == 'SYSDBA'
    
@login_required( login_url = '/login/' )
def invetariofisico_manageview( request, almacen_id = None, template_name = 'inventarios/inventarios_fisicos/inventariofisico.html' ):
    ''' Crea una vista de la pantalla para inventarios fisicos a puerta abierta por medio de ajustes '''

    connection_name = get_conecctionname( request.session )
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )
    almacen = Almacen.objects.get(pk=almacen_id)
    entrada, salida = ajustes_get_or_create(almacen_id = almacen_id, username = request.user.username)
    
    puede_modificar_costos = allow_microsipuser( username = request.user.username, clave_objeto = 469) and almacen.inventario_modifcostos
    form = DoctoInDetManageForm( request.POST or None )
    ubicacion_form = UbicacionArticulosForm(request.POST or None)

    sql = """select DISTINCT C.nombre, b.inv_fin_unid as existencia FROM 
            (select FIRST 20 DISTINCT b.articulo_id, b.nombre, a.sic_fechahora_u
            from doctos_in_det a, articulos b, doctos_in c
            where (b.articulo_id = a.articulo_id and c.docto_in_id = a.docto_in_id) and
                (c.almacen_id = %s and (c.concepto_in_id = 38 or c.concepto_in_id = 27 ) and c.cancelado = 'N' and c.descripcion = 'ES INVENTARIO')
            order by a.sic_fechahora_u DESC) C 
        left JOIN
         orsp_in_aux_art( articulo_id, '%s', '%s','%s','S','N') B
         on C.articulo_id = b.articulo_id
         """% (
                entrada.almacen.ALMACEN_ID, 
                entrada.almacen.nombre, 
                datetime.now().strftime( "01/01/%Y" ),
                datetime.now().strftime( "12/31/%Y" ),
                )
    
    articulos_rows = runsql_rows( sql, connection_name)
    articulos_contados = len( list( set(  InventariosDocumentoDetalle.objects.filter( Q(doctosIn__concepto = 27) | Q(doctosIn__concepto = 38) ).filter( 
        doctosIn__descripcion = 'ES INVENTARIO', 
        doctosIn__cancelado= 'N',
        doctosIn__almacen = entrada.almacen
        ).values_list( 'articulo', flat = True ) ) ))
    articulos = []
    for articulo in articulos_rows:
        articulos.append( { 'articulo' : articulo[0], 'unidades' : articulo[1], } )

    lineas_form = linea_articulos_form()
    c = { 
        'form' : form, 
        'articulos_contados': articulos_contados,
        'lineas_form': lineas_form,
        'puede_modificar_costos': puede_modificar_costos,
        'ubicacion_form' : ubicacion_form, 
        'articulos' : articulos, 
        'almacen' : entrada.almacen, 
        'almacen_id' : almacen_id,
        'entrada_fecha': entrada.fecha, 
        'folio_entrada': entrada.folio, 
        'folio_salida': salida.folio, 
        'entrada_id' : entrada.id,
        'salida_id' : salida.id,
        'is_mobile' : False,
        }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

@login_required( login_url = '/login/' )
def invetariofisicomobile_manageView( request, almacen_id = None, template_name = 'inventarios/inventarios_fisicos/mobile/inventariofisico.html' ):
    ''' Crea vista de panttalla para un inventario fisico a puerta abiera por ajustes pero con un diseño para un mobile '''
    connection_name = get_conecctionname(request.session)
    form = DoctoInDetManageForm( request.POST or None )

    entrada, salida = ajustes_get_or_create(almacen_id = almacen_id, username = request.user.username)
    puede_modificar_costos = allow_microsipuser( username = request.user.username, clave_objeto = 469)

    c = { 
        'form' : form,
        'puede_modificar_costos':puede_modificar_costos,
        'almacen' : entrada.almacen, 
        'almacen_id' : almacen_id,
        'entrada_fecha': entrada.fecha, 
        'folio_entrada': entrada.folio, 
        'folio_salida': salida.folio, 
        'entrada_id' : entrada.id,
        'salida_id' : salida.id,
        'is_mobile' : True,
        }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )    

@detect_mobile
@login_required( login_url = '/login/' )
def invetariosfisicos_view( request, template_name = 'inventarios/inventarios_fisicos/inventariosfisicos.html' ):
    ''' Muestra inventarios fisicos abiertos  '''

    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )
    
    inventarios_fisicos = InventariosDocumentoIF.objects.filter(aplicado='N', cancelado='N').order_by('-fecha')

    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False
       
    if request.mobile:
        url_inventario = '/inventarios/inventariofisicomobile/'
    else:
        url_inventario = '/inventarios/inventariofisico/'

    c = { 'inventarios_fisicos' : inventarios_fisicos, 'url_inventario' : url_inventario,}
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

def inventario_getnew_folio():
    ''' Obtiene el siguente folio automatico de un inventario '''

    registro_folioinventario = Registry.objects.get( nombre = 'SIG_FOLIO_INVFIS' )
    folio = registro_folioinventario.valor 
    siguiente_folio = "%09d" % ( int( folio ) +1 )
    registro_folioinventario.valor = siguiente_folio
    registro_folioinventario.save()
    return folio

@login_required( login_url = '/login/' )
def invetarioFisico_delete( request, id = None ):
    ''' Borra un inventario fisico '''

    inventario_fisico = get_object_or_404(InventariosDocumentoIF, pk=id)
    inventario_fisico.delete()

    return HttpResponseRedirect( '/invenatrios/InventariosFisicos/' )

##########################################
##                                      ##
##                ENTRADAS              ##
##                                      ##
##########################################

@login_required( login_url = '/login/' )
def entradas_View( request, template_name = 'inventarios/Entradas/entradas.html' ):
    entradas_list = InventariosDocumento.objects.filter( naturaleza_concepto = 'E' ).order_by( '-id' ) 

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

def recalcular_saldos_articulo( articulo_id, connection_name=None):
    ''' Funcion recalcular los saldos del articulo del detalle '''
    c = connections[ connection_name ].cursor()
    c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo_id )
    c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo_id )
    transaction.commit_unless_managed()
    management.call_command( 'syncdb', database = connection_name )

@login_required( login_url='/login/' )
def entrada_manageView( request, id = None, template_name='inventarios/Entradas/entrada.html' ):
    connection_name = get_conecctionname(request.session)
    message = ''
    nuevo = False
    hay_repetido = False
    if id:
        Entrada = get_object_or_404( InventariosDocumento, pk = id )
    else:
        Entrada = InventariosDocumento()
    
    initial_entrada = None
    if id:
        Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=0, can_delete=True)
    else:
        initial_entrada = { 'fecha': datetime.now(),}
        Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=1, can_delete=True)

    Entrada_form = EntradaManageForm( request.POST or None, instance = Entrada, initial = initial_entrada )
    EntradaItems_formset = Entrada_items(request.POST or None, instance=Entrada)

    if Entrada_form.is_valid() and EntradaItems_formset.is_valid():
        Entrada = Entrada_form.save(commit = False)
        #CARGA NUEVO ID
        if not Entrada.id:
            Entrada.naturaleza_concepto = 'E'
            Entrada.aplicado ='N'
            Entrada.save()
            nuevo = True
        else:
            Entrada.aplicado ='S'
            Entrada.save()

        articulos_recalculo = []
        #GUARDA ARTICULOS DE INVENTARIO FISICO
        for articulo_form in EntradaItems_formset:
            DetalleEntrada = articulo_form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not DetalleEntrada.id:
                DetalleEntrada.id = -1
                DetalleEntrada.almacen = Entrada.almacen
                DetalleEntrada.concepto = Entrada.concepto
                DetalleEntrada.doctosIn = Entrada
            articulos_recalculo.append(DetalleEntrada.articulo.id)

        EntradaItems_formset.save()

        if not nuevo:
            for articulo_id in articulos_recalculo:
                recalcular_saldos_articulo(articulo_id, connection_name)

        return HttpResponseRedirect('/inventarios/entradas')
    
    c = {'Entrada_form': Entrada_form, 'formset': EntradaItems_formset, 'message':message,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def entrada_delete(request, id = None):
    entrada = get_object_or_404(InventariosDocumento, pk=id)
    entrada.delete()

    return HttpResponseRedirect('/Entradas/')

##########################################
##                                      ##
##                SALIDAS               ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def salidas_View(request, template_name='inventarios/Salidas/salidas.html'):
    salidas_list = InventariosDocumento.objects.filter(naturaleza_concepto='S').order_by('-fecha') 

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
        Salida = get_object_or_404(InventariosDocumento, pk=id)
    else:
        Salida = InventariosDocumento()

    if request.method == 'POST':
        Salida_form = DoctosInManageForm(request.POST, request.FILES, instance=Salida)

        #PARA CARGAR DATOS DE EXCEL
        if 'excel' in request.POST:
            input_excel = request.FILES['file_inventario']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)
            articulos = Articulo.objects.filter(es_almacenable='S')

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

            
            articulos_enceros = Articulo.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
            
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
    salida = get_object_or_404(InventariosDocumento, pk=id)
    salida.delete()

    return HttpResponseRedirect('/Salidas/')

