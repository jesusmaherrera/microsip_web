#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from decimal import *
from microsip_web.libs.custom_db.main import get_conecctionname

from microsip_web.apps.config.models import *
from models import *
from forms import *
#ORDENES
def ordenes_view(request, template_name='compras/documentos/ordenes/ordenes.html'):

    try:
        ordenes_estado = Configuracion.objects.get(
            padre__padre__padre__nombre=request.user.username, 
            padre__nombre='VisorORDENES_COM', 
            nombre='Filtros').get_value().split(';')

        tipo = ordenes_estado[1]
        ordenes_estado = ordenes_estado[0]
    except ObjectDoesNotExist:
        ordenes_estado = u''
    
    if ordenes_estado ==u'':
        tipo = '&Todas las ordenes'

    #FILTRO
    documentos_list = DocumentoCompras.objects.filter(tipo='O')
    if not ordenes_estado == u'':
        documentos_list = documentos_list.filter(estado=ordenes_estado)
    documentos_list = documentos_list.order_by("-id")

    paginator = Paginator( documentos_list, 15 ) # Muestra 5 inventarios por pagina
    page = request.GET.get( 'page' )

    #####PARA PAGINACION##############
    try:
        documentos = paginator.page( page )
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        documentos = paginator.page( 1 )
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        documentos = paginator.page( paginator.num_pages )

    c = {'documentos':documentos, 'tipo':tipo[1:],}
    return render_to_response(template_name, c, context_instance=RequestContext(request))

def orden_manageview(request, id=None, template_name='compras/documentos/ordenes/orden.html'):


    connection_name = get_conecctionname(request.session)
    message = ''
    nuevo = False
    hay_repetido = False
    
    if id:
        documento = get_object_or_404( DocumentoCompras, pk = id )
    else:
        documento = DocumentoCompras()

    comprasdet_forms = DocumentoComprasDetalleFormset(DocumentoComprasDetalleManageForm, extra=1, can_delete=True)
    compradetalles_formset = comprasdet_forms(request.POST or None, instance=documento)
    

    documento_form = OrdenManageForm( request.POST or None, instance = documento)
    impuestos_form = DocumentoComprasImpuestosManageForm( request.POST or None)
    
    if documento_form.is_valid() and compradetalles_formset.is_valid() and impuestos_form.is_valid():
        
        documento = documento_form.save(commit=False)
        documento.tipo = 'C'
        documento.subtipo = 'N'
        documento.aplicado = 'N'
        documento.acreditar_cxp= 'N' 
        documento.contabilizado = 'N'
        documento.forma_emitida = 'N'
        
        documento.condicion_pago = documento.proveedor.condicion_de_pago
        importe_neto = 0
        for articulo_form in compradetalles_formset:
            importe_neto = importe_neto + articulo_form.cleaned_data['precio_total_neto']

        documento.importe_neto = importe_neto
        documento.save()

        #GUARDA ARTICULOS DE INVENTARIO FISICO
        for articulo_form in compradetalles_formset:
            detalle = articulo_form.save(commit = False)
            #PARA CREAR UNO NUEVO
            if not detalle.id:
                detalle.id = -1
                detalle.documento = documento

        compradetalles_formset.save()
    orden_id = None
    orden_id = documento.id
    
    c = {
        'documento_form':documento_form, 
        'formset':compradetalles_formset, 
        'impuestos_form':impuestos_form,
        'orden_id':orden_id,
        'documento_estado':documento.estado,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))
