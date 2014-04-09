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
from microsip_api.comun.sic_db import get_conecctionname, first_or_none

@login_required(login_url='/login/')
def facturas_view(request, template_name='ventas/documentos/facturas/facturas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    documentos_list = VentasDocumento.objects.filter(tipo='F').order_by('-fecha','cliente')

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
def factura_manageView( request, id = None, type='F', template_name='ventas/documentos/facturas/factura.html' ):
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

    if documento_detalle_formset.is_valid() and documento_form.is_valid():

        documento = documento_form.save(commit=False)

        cliente = documento.cliente
        cliente_clave = first_or_none( ClavesClientes.objects.filter( cliente= cliente ) )
        cliente_direccion =  first_or_none( ClienteDireccion.objects.filter( cliente= cliente ) )
        #Si es una documento nueva
        if not documento.id:
            documento_nuevo= True
            documento.caja= first_or_none( Caja.objects.all() )
            documento.tipo= 'F'
            documento.aplicado = 'N'
            documento.folio= ''#Se deja vacio para que se calcule el folio al guardar
            documento.fecha= datetime.now()
            documento.hora= datetime.now().strftime('%H:%M:%S')
            documento.cliente_clave= cliente_clave
            documento.cliente = cliente
            documento.cliente_direccion= cliente_direccion

            documento.moneda= Moneda.objects.get(pk= 1)
            documento.impuesto_incluido= 'N'
            documento.tipo_cambio= 1
            documento.descuento_tipo= 'I'

            #datos de documento global
            # documento.tipo_gen_fac='R'
            # documento.es_fac_global='S'
            # documento.fecha_ini_fac_global = fecha_ini_fac_global
            # documento.fecha_fin_fac_global = fecha_fin_fac_global

            documento.porcentaje_descuento=0
            
            documento.sistema_origen='VE'
            documento.usuario_creador= request.user.username
            documento.save()
            

        # # ventas_en_factura = documento_form.cleaned_data['ventas_en_factura']
        # # impuestos_venta_neta = documento_form.cleaned_data['impuestos_venta_neta'].split(',')
        # # impuestos_otros_impuestos = documento_form.cleaned_data['impuestos_otros_impuestos'].split(',')
        # # impuestos_importe_impuesto = documento_form.cleaned_data['impuestos_importe_impuesto'].split(',')
        # # impuestos_porcentaje_impuestos = documento_form.cleaned_data['impuestos_porcentaje_impuestos'].split(',')
        # # impuestos_ids = documento_form.cleaned_data['impuestos_ids'].split(',')

        # #Guardar impuestos
        # for impuesto_id, venta_neta, otros_impuestos, importe_impuesto, porcentaje_impuesto in zip(impuestos_ids, impuestos_venta_neta, impuestos_otros_impuestos, impuestos_importe_impuesto, impuestos_porcentaje_impuestos ):
        #     if impuesto_id != "":
        #         c = connections[connection_name].cursor()
        #         query =  '''INSERT INTO "IMPUESTOS_DOCTOS_PV" ("DOCTO_PV_ID", "IMPUESTO_ID", "VENTA_NETA", "OTROS_IMPUESTOS", "PCTJE_IMPUESTO", "IMPORTE_IMPUESTO") \
        #             VALUES (%s, %s, %s, %s, %s, %s)'''%(documento.id,  impuesto_id, venta_neta,  otros_impuestos, porcentaje_impuesto, importe_impuesto)
        #         c.execute(query)
        #         c.close()

        #Se guardan detalles de documento
        for detalle_form in documento_detalle_formset:
            detalle = detalle_form.save(commit = False)

            if not detalle.id:
                detalle.id = -1
                detalle.documento = documento
                detalle.unidades_surtidas_devueltas = 0
                detalle.fpgc_unitario = 0 
                detalle.comisiones_porcentaje = 0 
                detalle.rol = 'N' 
                detalle.posicion = -1
                detalle.save()

        message= 'documento guardada'

    c = {
        'documento_form': documento_form, 
        'documento_detalle_formset':documento_detalle_formset, 
        'message':message, 
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))