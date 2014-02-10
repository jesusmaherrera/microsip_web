#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required, permission_required
from decimal import *
from datetime import date, timedelta
from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from models import *
from .forms import *

def paises_view(request, template_name='main/otros/paises/paises.html'):

    paises = Pais.objects.all()

    PATH = request.path
    if '/punto_de_venta/paises/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/paises/' in PATH:
       	modulo = 'ventas'

    c = {
        'paises':paises, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def pais_manageView(request, id = None, template_name='main/otros/paises/pais.html'):
    message = ''
    PATH = request.path
    if '/punto_de_venta/pais/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/pais/' in PATH:
        modulo = 'ventas'

    if id:
        pais = get_object_or_404( Pais, pk=id)
    else:
        pais =  Pais()
    
    form = PaisManageForm(request.POST or None, instance=  pais)

    if form.is_valid():
        form.save()
        
        if '/punto_de_venta/pais/' in PATH:
            return HttpResponseRedirect('/punto_de_venta/paises/')
        elif '/ventas/pais/' in PATH:
            return HttpResponseRedirect('/ventas/paises/')    

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))