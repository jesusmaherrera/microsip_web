#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from .cliente_articulos.models import *
from .models import *
from .forms import *
from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none

@login_required(login_url='/login/')
def clientes_view(request, template_name='main/clientes/clientes/clientes.html'):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
        
    PATH = request.path
    if '/punto_de_venta/clientes/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/clientes/' in PATH:
        modulo = 'ventas'
        
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
    

    c = {
        'clientes':clientes, 
        'filtro_form':filtro_form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def cliente_manageView(request, id = None, template_name='main/clientes/clientes/cliente.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    PATH = request.path
    if '/punto_de_venta/cliente/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/cliente/' in PATH:
        modulo = 'ventas'

    message = ''

    if id:
        cliente = get_object_or_404(Cliente, pk=id)
        direccion = first_or_none(ClienteDireccion.objects.filter(cliente=cliente))
        if not direccion:
            direccion = ClienteDireccion()
    else:
        cliente =  Cliente()
        direccion = ClienteDireccion()

    direccion_form = DireccionClienteForm(request.POST or None, instance = direccion)
    form = ClienteManageForm(request.POST or None, instance=  cliente)
    
    if form.is_valid() and direccion_form.is_valid():
        clienteform =  form.save( commit = False )
        clienteform.usuario_ult_modif = request.user.username
        clienteform.save()
        direccion = direccion_form.save(commit=False)
        direccion.cliente = clienteform
        estado = direccion.ciudad.estado
        pais = estado.pais
        direccion.nombre_consignatario = u'Dirección principal'

        direccion.calle = '''%s %s %s,
        %s%s,
        %s
        '''%(direccion.calle_nombre, direccion.numero_exterior, direccion.numero_interior, direccion.colonia, direccion.poblacion, direccion.referencia)
        direccion.estado = estado
        direccion.pais= pais
        direccion.es_ppal = 'S'
        direccion.save()
        return HttpResponseRedirect('/%s/clientes/'%modulo)
    
    cliente_articulos = ClienteArticulo.objects.filter(cliente=id)
    c = {
        'cliente_articulos':cliente_articulos,
        'form':form, 
        'direccion_form':direccion_form, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))