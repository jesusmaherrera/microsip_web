#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from .forms import *
from microsip_web.libs.custom_db.main import get_conecctionname

@login_required(login_url='/login/')
def condiciones_de_pago_view(request, template_name='main/clientes/condiciones_de_pago/condiciones_de_pago.html'):
    ''' Para listar todas las condiciones de pago. '''

    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    PATH = request.path
    if '/punto_de_venta/condiciones_de_pago/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/condiciones_de_pago/' in PATH:
        modulo = 'ventas'
        
    msg = ''
    
    condiciones_de_pago_list = CondicionPago.objects.all().order_by('nombre')
    
    paginator = Paginator(condiciones_de_pago_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        condiciones_de_pago = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        condiciones_de_pago = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        condiciones_de_pago = paginator.page(paginator.num_pages)
    
    c = {
        'condiciones_de_pago':condiciones_de_pago, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def condicion_de_pago_manageView(request, id = None, template_name='main/clientes/condiciones_de_pago/condicion_de_pago.html'):
    conexion_activa_id = request.session['conexion_activa']
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
    conexion_base_datos = "%02d-%s"%(conexion_activa_id, basedatos_activa)

    PATH = request.path
    if '/punto_de_venta/condicion_de_pago/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/condicion_de_pago/' in PATH:
        modulo = 'ventas'

    message = ''

    if id:
        condicion_de_pago = get_object_or_404(CondicionPago, pk=id)
    else:
        condicion_de_pago =  CondicionPago()

    form = CondicionPagoManageForm(request.POST or None, instance=  condicion_de_pago)
    plazo_forms = CondicionPagoPlazoFormset(CondicionPagoPlazoManageForm, extra=1, can_delete=True)
    plazo_formset = plazo_forms(request.POST or None, instance=condicion_de_pago)
    
    if form.is_valid() and plazo_formset.is_valid():

        condicion_pago = form.save(commit=False)
        condicion_pago.usuario_creador = request.user.username
        condicion_pago.usuario_ult_modif = condicion_pago.usuario_creador
        condicion_pago.save()
        plazo_formset.save()

        return HttpResponseRedirect('/%s/condiciones_de_pago/'%modulo)
    
    c = {
        'form':form, 
        'plazo_formset':plazo_formset,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))


