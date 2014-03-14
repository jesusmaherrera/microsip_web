#encoding:utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# user autentication
from django.contrib.auth.decorators import login_required
from models import *
# from forms import *
from microsip_api.comun.sic_db import get_conecctionname

@login_required(login_url='/login/')
def remisiones_view(request, template_name='ventas/documentos/remisiones/remisiones.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    documentos_list = VentasDocumento.objects.filter(tipo='R').order_by('-id')

    paginator = Paginator(documentos_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        documentos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documentos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documentos = paginator.page(paginator.num_pages)

    c = {'documentos':documentos,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))