 #encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import inlineformset_factory

#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from django.utils.encoding import smart_str, smart_unicode

from django.db import connection, transaction
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import formset_factory
import datetime, time
import xlrd

from models import *
from forms import *
from microsip_web.libs.custom_db.main import next_id
from triggers import triggers

##########################################
##                                      ##
##               LOGIN                  ##
##                                      ##
##########################################

def inicializar_tablas(request):
    c = connection.cursor()
    #ENTRADAS Y SALIDAS DE INVENTARIOS
    c.execute(triggers['SIC_PUERTA_INV_DESGLOSEDIS_AI'])
    c.execute(triggers['SIC_PUERTA_INV_DOCTOSINDET_BI'])
    c.execute(triggers['SIC_PUERTA_INV_DOCTOSINDET_BD'])
    
    c.execute(triggers['SIC_PUERTA_INV_DOCTOSIN_BU'])
    
    
    transaction.commit_unless_managed()

    return HttpResponseRedirect('/inventarios/InventariosFisicos/')

def ingresar(request):
    # if not request.user.is_anonymous():
    #   return HttpResponseRedirect('/')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        

        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/')
                else:
                    return render_to_response('noactivo.html', context_instance=RequestContext(request))
            else:
                return render_to_response('main/login.html',{'form':formulario, 'message':'Nombre de usaurio o password no validos',}, context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('main/login.html',{'form':formulario, 'message':'',}, context_instance=RequestContext(request))

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')

def c_get_next_key(seq_name):
    """ return next value of sequence """
    c = connection.cursor()
    c.execute("SELECT GEN_ID( ID_DOCTOS , 1 ) FROM RDB$DATABASE;")
    row = c.fetchone()
    return int(row[0])

##########################################
##                                      ##
##        INVENTARIOS FISICOS           ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def invetariosFisicos_View(request, template_name='inventarios/Inventarios Fisicos/inventarios_fisicos.html'):
    inventarios_fisicos_list = DoctosInvfis.objects.filter(aplicado='N', cancelado='N').order_by('-fecha') 

    paginator = Paginator(inventarios_fisicos_list, 15) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        inventarios_fisicos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        inventarios_fisicos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        inventarios_fisicos = paginator.page(paginator.num_pages)

    c = {'inventarios_fisicos':inventarios_fisicos}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

def split_seq(seq, n):
    """ Yield successive n-sized chunks from l.
    """
    lista = []
    for i in xrange(0, len(seq), n):
        lista.append(seq[i:i+n])
    return lista

@login_required(login_url='/login/')
def add_articulos_nocontabilizados_porlinea(request, inventario_id = None, linea_id= None):
    inventario_fisico = DoctosInvfis.objects.get(pk=inventario_id)
    linea = LineaArticulos.objects.get(pk=linea_id)
    articulos_enInventario = DoctosInvfisDet.objects.filter(docto_invfis=inventario_fisico).order_by('-articulo').values_list('articulo__id', flat=True)
    articulos_enceros = Articulos.objects.filter(es_almacenable='S',linea=linea).exclude(pk__in=articulos_enInventario).order_by('-id').values_list('id', flat=True)[0:9000]
    
    articulos_enceros_list = split_seq(articulos_enceros, 2000)
    
    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter(articulo__id=articulo_id)
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario =DoctosInvfisDet(
                id=-1,
                docto_invfis= inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get(pk=articulo_id),
                unidades = 0)


            detalles_en_ceros.append(detalle_inventario)
    
        DoctosInvfisDet.objects.bulk_create(detalles_en_ceros)

    return HttpResponseRedirect('/inventarios/InventarioFisico_pa/%s'% inventario_id)

@login_required(login_url='/login/')
def add_articulos_nocontabilizados(request, id = None):
    inventario_fisico = DoctosInvfis.objects.get(pk=id)
    articulos_enInventario = DoctosInvfisDet.objects.filter(docto_invfis=inventario_fisico).order_by('-articulo').values_list('articulo__id', flat=True)
    articulos_enceros = Articulos.objects.filter(es_almacenable='S').exclude(pk__in=articulos_enInventario).order_by('-id').values_list('id', flat=True)[0:9000]
    
    articulos_enceros_list = split_seq(articulos_enceros, 2000)
    
    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter(articulo__id=articulo_id)
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario =DoctosInvfisDet(
                id=-1,
                docto_invfis= inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get(pk=articulo_id),
                unidades = 0)


            detalles_en_ceros.append(detalle_inventario)
    
        DoctosInvfisDet.objects.bulk_create(detalles_en_ceros)

    return HttpResponseRedirect('/inventarios/InventarioFisico_pa/%s'% id)

def inventario_getnew_folio():
    registro_folioinventario = Registry.objects.get(nombre='SIG_FOLIO_INVFIS')
    folio = registro_folioinventario.valor 
    siguiente_folio = "%09d" % (int(folio) +1)
    registro_folioinventario.valor = siguiente_folio
    registro_folioinventario.save()
    return folio

@login_required(login_url='/login/')
def create_invetarioFisico_pa_createView(request, template_name='inventarios/Inventarios Fisicos/create_inventario_fisico_pa.html'):
    message = ''
    if request.method == 'POST':
        form = DoctoInvfis_CreateForm(request.POST)
        if form.is_valid():
            folio = inventario_getnew_folio()
            inventario = form.save(commit= False)
            inventario.id =-1
            inventario.folio = folio
            inventario.usuario_creador ='SYSDBA'
            inventario.usuario_aut_creacion ='SYSDBA'
            inventario.usuario_ult_modif ='SYSDBA'
            inventario.usuario_aut_modif ='SYSDBA'
            inventario.save()
            return HttpResponseRedirect('/inventarios/InventariosFisicos/')

    else:
        form = DoctoInvfis_CreateForm()

    c = {
        'message':message,
        'form':form,
        }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def invetarioFisico_pa_manageView(request, id = None, rapido=1, template_name='inventarios/Inventarios Fisicos/inventario_fisico_pa.html'):
    message = ''
    msg_series=''
    error = 0
    inicio_form = False
    movimiento = ''

    InventarioFisico = get_object_or_404(DoctosInvfis, pk=id)
    detallesInventario = DoctosInvfisDet.objects.filter(docto_invfis=InventarioFisico).order_by('-id')
    articulos_discretos_formset = formset_factory(ArticulosDiscretos_ManageForm)
    articulos_discretos_actuales= []
    #POST
    if request.method == 'POST':
        detalleInvForm = DoctosInvfisDetManageForm(request.POST)
        if detalleInvForm.is_valid():
            articulos_discretos_formset = articulos_discretos_formset(request.POST, request.FILES)
            detalleInv = detalleInvForm.save(commit=False)  
            unidades = abs(detalleInv.unidades)
            total_forms = abs(articulos_discretos_formset.total_form_count())
            if detalleInv.articulo.seguimiento == 'L':
                message = 'La aplicacion no esta preparada para trabajar con articulos de lotes, porfavor introduce estos articulos directamente en microsip'
                error = 1

            #Para cargar por primera ves el formset de los nuemeros de serie del articulo
            if detalleInv.articulo.seguimiento == 'S':
                if detalleInv != '':
                    doc_det = DoctosInvfisDet.objects.filter(docto_invfis=InventarioFisico, articulo=detalleInv.articulo)
                    if doc_det.count() > 0:
                        articulos_discretos_actuales = DesgloseEnDiscretosInvfis.objects.filter(
                        docto_invfis_det=doc_det[0].id)

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
                if articulos_discretos_formset.is_valid() and (articulos_discretos_formset.total_form_count() > 0 or detalleInv.articulo.seguimiento == 'N'):
                    unidades = 0
                    try:
                        doc = DoctosInvfisDet.objects.get(docto_invfis=InventarioFisico, articulo=detalleInv.articulo)
                        id_detalle = doc.id
                        if 'add_button' in request.POST:
                            unidades = doc.unidades + detalleInv.unidades
                        else:
                            unidades = doc.unidades - detalleInv.unidades
                        
                        if unidades <= 0:
                            movimiento = 'eliminar'
                        else:
                            movimiento = 'actualizar'

                    except ObjectDoesNotExist:
                        if detalleInv.unidades >= 0:
                            id_detalle = c_get_next_key('ID_DOCTOS')
                            detalleInv.id = id_detalle
                            articulos_claves =ClavesArticulos.objects.filter(articulo= detalleInv.articulo)
                            
                            if articulos_claves.count() < 1:
                                articulo_clave = ''
                            else:
                                articulo_clave = articulos_claves[0].clave

                            detalleInv.clave = articulo_clave
                            detalleInv.docto_invfis = InventarioFisico
                            movimiento = 'crear'
                    
                    if detalleInv.articulo.seguimiento == 'S':    
                        for form in articulos_discretos_formset.forms:
                            form = form.save(commit=False)
                            art_discreto = ArticulosDiscretos.objects.filter(articulo = form.articulo, clave = form.clave)

                            if art_discreto.count() > 0:
                                art_discreto = art_discreto[0]
                            else:
                                art_discreto = ArticulosDiscretos.objects.create(id=next_id('ID_CATALOGOS'), clave = form.clave, articulo = form.articulo, tipo='S', fecha= None)        

                            if DesgloseEnDiscretosInvfis.objects.filter(art_discreto = art_discreto).exists() and detalleInv.unidades > 0:
                                msg_series = 'Ya existe un articulo registrado en inventario con numero de serie [%s]'%form.clave
                                error = 1                                
                            if error == 0:
                                if detalleInv.unidades > 0 :
                                    if movimiento == 'crear':
                                        detalleInv.save()

                                    desglose = DesgloseEnDiscretosInvfis(
                                        id = -1,
                                        docto_invfis_det = DoctosInvfisDet.objects.get(id=id_detalle),
                                        art_discreto = art_discreto,
                                        unidades = 1,
                                        )
                                    desglose.save()
                                else:
                                    desgloses_a_eliminar = DesgloseEnDiscretosInvfis.objects.filter(art_discreto=art_discreto)
                                    
                                    if desgloses_a_eliminar.count() <= 0:
                                        error = 2
                                        msg_series = 'No extiste registrado un articulo con este numero de serie en el inventario, no se eliminara'
                                    else:
                                        desgloses_a_eliminar.delete()
                    if error == 0:
                        if movimiento == 'crear':
                            detalleInv.save()
                        elif movimiento == 'eliminar':                        
                            DoctosInvfisDet.objects.filter(id=id_detalle).delete()
                        elif movimiento == 'actualizar':
                            DoctosInvfisDet.objects.filter(id=id_detalle, articulo=detalleInv.articulo).update(unidades=unidades)

                        return HttpResponseRedirect('/inventarios/InventarioFisico_pa/%s/'% id)
                           
    else:
        detalleInvForm = DoctosInvfisDetManageForm()
        
        articulos_discretos_formset = formset_factory(ArticulosDiscretos_ManageForm)    
        data = {
            'form-TOTAL_FORMS': u'0',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
        articulos_discretos_formset = articulos_discretos_formset(data)
    
    articulos_eninventario = detallesInventario.count()
    paginator = Paginator(detallesInventario, 30) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        detallesInventario = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        detallesInventario = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        detallesInventario = paginator.page(paginator.num_pages)

    lineas_form = linea_articulos_form()


    c = {
        'message':message,
        'lineas_form':lineas_form,
        'inicio_form':inicio_form, 
        'msg_series':msg_series, 
        'detallesInventario':detallesInventario,
        'detalleInvForm':detalleInvForm, 
        'InventarioFisico':InventarioFisico,
        'formset':articulos_discretos_formset,
        'inventario_id':id,
        'articulos_eninventario':articulos_eninventario,
        'articulos_discretos_actuales':articulos_discretos_actuales,
        }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def invetarioFisico_manageView(request, id = None, template_name='inventarios/Inventarios Fisicos/inventario_fisico.html'):
    message = ''
    hay_repetido = False
    if id:
        InventarioFisico = get_object_or_404(DoctosInvfis, pk=id)
    else:
        InventarioFisico = DoctosInvfis()

    if request.method == 'POST':
        InventarioFisico_form = DoctosInvfisManageForm(request.POST, request.FILES, instance=InventarioFisico)

        #PARA CARGAR DATOS DE EXCEL
        if 'excel' in request.POST:
            input_excel = request.FILES['file_inventario']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)
            articulos = Articulos.objects.filter(es_almacenable='S')

            inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=articulos.count(), can_delete=True)
            
            lista = []
            lista_articulos = []        

            for i in range(sheet.nrows):
                clave_articulo = get_object_or_404(ClavesArticulos, clave=sheet.cell_value(i,0))
                if clave_articulo and clave_articulo.articulo.es_almacenable=='S':
                    if clave_articulo.articulo.id in lista_articulos:
                        message = 'El Articulo [%s] con clave [%s] esta repetido en el archivo de excel por favor corrigelo para continuar '% (clave_articulo.articulo.nombre, clave_articulo.clave)
                        hay_repetido = True
                    lista.append({'articulo': clave_articulo.articulo, 'unidades':int(sheet.cell_value(i,1)),})
                    lista_articulos.append(clave_articulo.articulo.id)

            
            articulos_enceros = Articulos.objects.exclude(pk__in=lista_articulos).filter(es_almacenable='S')
            
            for i in articulos_enceros:
                
                #clave_articulo = ClavesArticulos.objects.filter(articulo__id=i.id)
                articulosclav = ClavesArticulos.objects.filter(articulo__id=i.id)
                if articulosclav:
                    lista.append({'articulo': i, 'clave':articulosclav[0].clave , 'unidades':0,})   
                else:
                    lista.append({'articulo': i, 'clave':'', 'unidades':0,})    

            InventarioFisicoItems_formset = inventarioFisico_items(initial=lista)
        #GUARDA CAMBIOS EN INVENTARIO FISICO
        else:
            inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
            InventarioFisicoItems_formset = inventarioFisico_items(request.POST, request.FILES, instance=InventarioFisico)
            
            if InventarioFisico_form.is_valid() and InventarioFisicoItems_formset.is_valid():
                inventarioFisico = InventarioFisico_form.save(commit = False)

                #CARGA NUEVO ID
                if not inventarioFisico.id:
                    inventarioFisico.id = c_get_next_key('ID_DOCTOS')
                
                inventarioFisico.save()

                #GUARDA ARTICULOS DE INVENTARIO FISICO
                for articulo_form in InventarioFisicoItems_formset:
                    DetalleInventarioFisico = articulo_form.save(commit = False)
                    #PARA CREAR UNO NUEVO
                    if not DetalleInventarioFisico.id:
                        DetalleInventarioFisico.id = -1
                        DetalleInventarioFisico.docto_invfis = inventarioFisico
                
                InventarioFisicoItems_formset.save()
                return HttpResponseRedirect('/inventarios/InventariosFisicos/')
    else:
        inventarioFisico_items = inventarioFisico_items_formset(DoctosInvfisDetManageForm, extra=1, can_delete=True)
        InventarioFisico_form= DoctosInvfisManageForm(instance=InventarioFisico)
        InventarioFisicoItems_formset = inventarioFisico_items(instance=InventarioFisico)
    
    c = {'InventarioFisico_form': InventarioFisico_form, 'formset': InventarioFisicoItems_formset, 'message':message,}

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def invetarioFisico_delete(request, id = None):
    inventario_fisico = get_object_or_404(DoctosInvfis, pk=id)
    inventario_fisico.delete()

    return HttpResponseRedirect('/invenatrios/InventariosFisicos/')

##########################################
##                                      ##
##                ENTRADAS              ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def entradas_View(request, template_name='inventarios/Entradas/entradas.html'):
    entradas_list = DoctosIn.objects.filter(naturaleza_concepto='E').order_by('-fecha') 

    paginator = Paginator(entradas_list, 15) # Muestra 5 inventarios por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        entradas = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entradas = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entradas = paginator.page(paginator.num_pages)

    c = {'entradas':entradas}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def entrada_manageView(request, id = None, template_name='inventarios/Entradas/entrada.html'):
    message = ''
    hay_repetido = False
    if id:
        Entrada = get_object_or_404(DoctosIn, pk=id)
    else:
        Entrada = DoctosIn()

    if request.method == 'POST':
        Entrada_form = DoctosInManageForm(request.POST, request.FILES, instance=Entrada)

        #PARA CARGAR DATOS DE EXCEL
        if 'excel' in request.POST:
            input_excel = request.FILES['file_inventario']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)
            articulos = Articulos.objects.filter(es_almacenable='S')

            Entrada_items = doctoIn_items_formset(DoctosInDetManageForm, extra=articulos.count(), can_delete=True)
            
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

