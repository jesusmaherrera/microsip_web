#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required, permission_required

from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from .models import Ciudad, Estado
from .forms import *

@login_required(login_url='/login/')
def ciudades_view(request, template_name='main/otros/ciudades/ciudades.html'):

    ciudades = Ciudad.objects.all()

    PATH = request.path
    if '/punto_de_venta/ciudades/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/ciudades/' in PATH:
       	modulo = 'ventas'

    c = {
        'ciudades':ciudades, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def ciudad_manageView(request, id = None, template_name='main/otros/ciudades/ciudad.html'):
    message = ''
    PATH = request.path
    if '/punto_de_venta/ciudad/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/ciudad/' in PATH:
        modulo = 'ventas'

    if id:
        ciudad = get_object_or_404( Ciudad, pk=id)
    else:
        ciudad =  Ciudad()
    
    form = CiudadManageForm(request.POST or None, instance=  ciudad)

    if form.is_valid():
        form.save()
        
        if '/punto_de_venta/ciudad/' in PATH:
            return HttpResponseRedirect('/punto_de_venta/ciudades/')
        elif '/ventas/ciudad/' in PATH:
            return HttpResponseRedirect('/ventas/ciudades/')    

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))