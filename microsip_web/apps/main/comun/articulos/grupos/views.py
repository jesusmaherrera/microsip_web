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

@login_required(login_url='/login/')
def grupos_lineas_view(request, template_name='main/articulos/grupos/grupos.html'):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
    PATH = request.path
    if '/punto_de_venta/grupos/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/grupos/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/grupos/' in PATH:
        modulo = 'inventarios'

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

    c = {
        'grupos_lineas':grupos_lineas,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def grupo_lineas_manageView(request, id = None, template_name='main/articulos/grupos/grupo.html'):
    message = ''

    if id:
        grupo_lineas = get_object_or_404( GrupoLineas, pk=id)
    else:
        grupo_lineas =  GrupoLineas()
    
    PATH = request.path
    if '/punto_de_venta/grupo/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/grupo/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/grupo/' in PATH:
        modulo = 'inventarios'

    if request.method == 'POST':
        form = GrupoLineasManageForm(request.POST, instance=  grupo_lineas)
        if form.is_valid():
            grupo = form.save()
            return HttpResponseRedirect('/%s/grupos'%modulo)
    else:
        form = GrupoLineasManageForm(instance= grupo_lineas)

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))