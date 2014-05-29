#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from mobi.decorators import detect_mobile
from .models import *
from .forms import *
from django.db.models import Q
from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from django.forms.models import modelformset_factory
from django.core.exceptions import FieldError

@detect_mobile
@login_required(login_url='/login/')
def articulos_view(request, carpeta=1,template_name='main/articulos/articulos/articulos.html'):
    almacenes = Almacen.objects.all()
    
    articulos_porpagina = 50  
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    if "Chrome" in request.META['HTTP_USER_AGENT']:
        request.mobile = False
       
    if request.mobile:
        url_articulo = '/inventarios/articulo/'
        articulos_porpagina = 5    
    else:
        url_articulo = '/punto_de_venta/articulo/'
    
    PATH = request.path
    if '/punto_de_venta/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/' in PATH:
        modulo = 'inventarios'
    url_articulo = '/%s/articulo/'%modulo

    msg = ''
    if request.method =='POST':
        filtro_form = filtroarticulos_form(request.POST)
        if filtro_form.is_valid():
            articulo = filtro_form.cleaned_data['articulo']
            nombre = filtro_form.cleaned_data['nombre']
            clave = filtro_form.cleaned_data['clave']

            if articulo != None:
                return HttpResponseRedirect('%s%s/'% (url_articulo, articulo.id))
            elif clave != '':
                clave_articulo = ArticuloClave.objects.filter(clave=clave)
                if clave_articulo.count() > 0:
                    return HttpResponseRedirect('%s%s/'% (url_articulo, clave_articulo[0].articulo.id))
                else:
                    articulos_list = Articulo.objects.filter(nombre__icontains=nombre).order_by('nombre')
                    msg='No se encontro ningun articulo con esta clave'
            else:
                articulos_list = Articulo.objects.filter(nombre__icontains=nombre).order_by('nombre')
    else:
        filtro_form = filtroarticulos_form()
        try:
            Articulo._meta.get_field_by_name('carpeta')
        except:
            articulos_list = Articulo.objects.all().order_by('nombre') #filter(carpeta = carpeta)
        else:
            articulos_list = Articulo.objects.filter(Q(carpeta__id=carpeta)| Q(carpeta__id=None)).order_by('nombre') #filter(carpeta = carpeta)
    
    paginator = Paginator(articulos_list, articulos_porpagina) # Muestra 10 ventas por pagina
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
    
    c = {
        'articulos':articulos,
        'carpeta':carpeta,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
        'filtro_form':filtro_form,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def articulo_manageview(request, id, template_name='main/articulos/articulos/articulo.html'):
    ''' Modificacion de datos de un articulo '''
    conexion_activa_id = request.session['conexion_activa']
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
    conexion_base_datos = "%02d-%s"%(conexion_activa_id, basedatos_activa)

    PATH = request.path
    if '/punto_de_venta/articulo/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/articulo/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/articulo/' in PATH:
        modulo = 'inventarios'
   
    articulo = get_object_or_404(Articulo, pk=id)

    clavesarticulos_fromset = modelformset_factory(ArticuloClave, form= claves_articulos_form, can_delete=True,)
    preciosarticulos_fromset = modelformset_factory(ArticuloPrecio, form= precios_articulos_form, can_delete=True,)

    impuestos_articulo = ImpuestosArticulo.objects.filter(articulo=articulo)
    if impuestos_articulo.count() > 0:
        impuesto_articulo = impuestos_articulo[0]
    else:
        impuesto_articulo = ImpuestosArticulo()
    
    if request.method == 'POST':
        formset = clavesarticulos_fromset(request.POST, prefix="formset")
        precios_formset = preciosarticulos_fromset(request.POST, prefix="precios_formset")
    else:
        formset = clavesarticulos_fromset(queryset=ArticuloClave.objects.filter(articulo=articulo), prefix="formset")
        precios_formset = preciosarticulos_fromset(queryset=ArticuloPrecio.objects.filter(articulo=articulo), prefix="precios_formset")

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

        return HttpResponseRedirect('/%s/articulos/'%modulo)


    c = {
        'articulo_form':articulo_form,
        'precios_formset':precios_formset,
        'impuesto_articulo_form':impuesto_articulo_form,
        'formset':formset,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    } 
    return render_to_response(template_name, c, context_instance=RequestContext(request))

# @login_required(login_url='/login/')
# def cliente_manageView(request, id = None, template_name='main/clientes/clientes/cliente.html'):
#     connection_name = get_conecctionname(request.session)
#     if connection_name == '':
#         return HttpResponseRedirect('/select_db/')

#     PATH = request.path
#     if '/punto_de_venta/cliente/' in PATH:
#         modulo = 'punto_de_venta'
#     elif '/ventas/cliente/' in PATH:
#         modulo = 'ventas'

#     message = ''

#     if id:
#         cliente = get_object_or_404(Cliente, pk=id)
#         direccion = first_or_none(ClienteDireccion.objects.filter(cliente=cliente))
#         if not direccion:
#             direccion = ClienteDireccion()
#     else:
#         cliente =  Cliente()
#         direccion = ClienteDireccion()

#     direccion_form = DireccionClienteForm(request.POST or None, instance = direccion)
#     form = ClienteManageForm(request.POST or None, instance=  cliente)
    
#     if form.is_valid() and direccion_form.is_valid():
#         clienteform =  form.save( commit = False )
#         clienteform.usuario_ult_modif = request.user.username
#         clienteform.save()
#         direccion = direccion_form.save(commit=False)
#         direccion.cliente = clienteform
#         estado = direccion.ciudad.estado
#         pais = estado.pais
#         direccion.estado = estado
#         direccion.pais= pais
#         direccion.save()
#         return HttpResponseRedirect('/%s/clientes/'%modulo)
    
#     c = {
#         'form':form, 
#         'direccion_form':direccion_form, 
#         'extend':'%s/base.html'%modulo,
#         'modulo':modulo,
#     }
#     return render_to_response(template_name, c, context_instance=RequestContext(request))