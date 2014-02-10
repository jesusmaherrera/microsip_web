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
def lineas_articulos_view(request, template_name='main/articulos/lineas/lineas.html'):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    PATH = request.path
    if '/punto_de_venta/lineas/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/lineas/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/lineas/' in PATH:
        modulo = 'inventarios'
    
    linea_articulos_list = LineaArticulos.objects.all()

    paginator = Paginator(linea_articulos_list, 50) # Muestra 10 ventas por pagina
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

    c = {
        'lineas_articulos':lineas_articulos,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def linea_articulos_manageView(request, id = None, template_name='main/articulos/lineas/linea.html'):
    message = ''
    PATH = request.path
    if '/punto_de_venta/linea/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/linea/' in PATH:
        modulo = 'ventas'
    elif '/inventarios/linea/' in PATH:
        modulo = 'inventarios'

    if id:
        linea_articulos = get_object_or_404( LineaArticulos, pk=id)
    else:
        linea_articulos =  LineaArticulos()
    
    if request.method == 'POST':
        form = LineaArticulosManageForm(request.POST, instance=  linea_articulos)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/%s/lineas'%modulo)
    else:
        form = LineaArticulosManageForm(instance= linea_articulos)

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))
