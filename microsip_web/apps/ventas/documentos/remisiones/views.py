#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# user autentication
from django.contrib.auth.decorators import login_required
from models import *
from forms import *
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

@login_required( login_url='/login/' )
def remision_manageview( request, id = None, template_name='ventas/documentos/remisiones/remision.html' ):
    message = ''
    connection_name = get_conecctionname(request.session)
    documento_nuevo = False
    
    if id:
        documento = get_object_or_404( VentasDocumento, pk = id )
    else:
        documento = VentasDocumento()

    #Cargar formularios
    if id:
        documento_form = VentasDocumentoForm( request.POST or None, instance = documento,)
        documento_items = VentasDocumentoDetalleFormSet(VentasDocumentoDetalleForm, extra=0, can_delete=False)
    else:
        initial_data = { 'fecha': datetime.now(),}
        documento_form = VentasDocumentoForm( request.POST or None, instance = documento, initial= initial_data)
        documento_items = VentasDocumentoDetalleFormSet(VentasDocumentoDetalleForm, extra=1, can_delete=False)
        
    documento_detalle_formset = documento_items(request.POST or None, instance=documento)

    c = {
        'documento_form': documento_form, 
        'documento_detalle_formset':documento_detalle_formset, 
        'message':message, 
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))