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

def impuestos_view(request, template_name='main/listas/impuestos/impuestos.html'):

    impuestos = Impuesto.objects.all()

    PATH = request.path
    if '/punto_de_venta/impuestos/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/impuestos/' in PATH:
       	modulo = 'ventas'

    c = {
        'impuestos':impuestos, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def impuesto_manageView(request, id = None, template_name='main/listas/impuestos/impuesto.html'):
    message = ''
    PATH = request.path
    if '/punto_de_venta/impuesto/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/impuesto/' in PATH:
        modulo = 'ventas'

    if id:
        impuesto = get_object_or_404( Impuesto, pk=id)
    else:
        impuesto =  Impuesto()
    
    form = ImpuestoManageForm(request.POST or None, instance=  impuesto)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/%s/impuestos/'%modulo)
        

    c = {
        'form':form,
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }
    return render_to_response(template_name, c, context_instance=RequestContext(request))