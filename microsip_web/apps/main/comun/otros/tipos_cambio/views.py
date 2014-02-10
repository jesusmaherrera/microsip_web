#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.base import View
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from .forms import *

def tipos_cambio_view(request, template_name='main/otros/tipos_cambio/tipos_cambio.html'):

    tipos_cambio_list = TipoCambio.objects.all()

    paginator = Paginator(tipos_cambio_list, 15) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        tipos_cambio = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tipos_cambio = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tipos_cambio = paginator.page(paginator.num_pages)

    PATH = request.path
    if '/punto_de_venta/tipos_cambio/' in PATH:
        modulo = 'punto_de_venta'
    elif '/ventas/tipos_cambio/' in PATH:
       	modulo = 'ventas'

    c = {
        'tipos_cambio':tipos_cambio, 
        'extend':'%s/base.html'%modulo,
        'modulo':modulo,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))