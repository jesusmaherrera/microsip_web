#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required, permission_required

from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from .models import Estado, Pais
from .forms import *

@login_required(login_url='/login/')
def estados_view(request, template_name='main/otros/estados/estados.html'):

    estados = Estado.objects.all()

    PATH = request.path
    if '/punto_de_venta/estados/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/estados/' in PATH:
       	modulo = 'ventas'

    c = {
        'estados':estados, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def estado_manageView(request, id = None, template_name='main/otros/estados/estado.html'):
    message = ''
    PATH = request.path
    if '/punto_de_venta/estado/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/estado/' in PATH:
        modulo = 'ventas'

    if id:
        estado = get_object_or_404( Estado, pk=id)
    else:
        estado =  Estado()
    
    form = EstadoManageForm(request.POST or None, instance=  estado)

    if form.is_valid():
        form.save()
        
        if '/punto_de_venta/estado/' in PATH:
            return HttpResponseRedirect('/punto_de_venta/estados/')
        elif '/ventas/estado/' in PATH:
            return HttpResponseRedirect('/ventas/estados/')    

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))