#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from decimal import *
from datetime import date, timedelta
from microsip_web.libs.custom_db.main import get_conecctionname, first_or_none
from models import *
from forms import *

def compras_view(request, template_name='compras/documentos/compras/compras.html'):


    compras_list = DocumentoCompras.objects.filter(tipo='C').order_by("-id")

    paginator = Paginator( compras_list, 15 ) # Muestra 5 inventarios por pagina
    page = request.GET.get( 'page' )

    #####PARA PAGINACION##############
    try:
        compras = paginator.page( page )
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        compras = paginator.page( 1 )
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        compras = paginator.page( paginator.num_pages )

    
    c = {
        'compras':compras, 
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))


def compra_manageview(request, id=None, type='C', template_name='compras/documentos/compras/compra.html'):

    connection_name = get_conecctionname(request.session)
    message = ''
    nuevo = False
    hay_repetido = False
    
    if id:
        documento = get_object_or_404( DocumentoCompras, pk = id )
    else:
        documento = DocumentoCompras()

    #Para crear compra de una orden
    documento_fte = None
    initial_form = None
    initial_formset=[]
    initial_impuestos={}
    if type == 'O' and id:
        documento_fte =  documento
        initial_form = {
            'fecha':documento.fecha,
            'proveedor':documento.proveedor,
            'condicion_pago':documento.condicion_pago,
            'almacen': documento.almacen,
            'moneda':documento.moneda,
            'total_impuestos':documento.total_impuestos,
            'total_retenciones':documento.total_retenciones,
        }

        initial_formset=[]

        detalles = DocumentoComprasDetalle.objects.filter(documento=documento)
        for detalle in detalles:
            initial_formset.append({
                    'articulo':detalle.articulo,
                    'umed':detalle.umed,
                    'unidades':detalle.unidades,
                    'clave_articulo':detalle.clave_articulo,
                    'precio_unitario':detalle.precio_unitario,
                    'precio_total_neto':detalle.precio_total_neto,
                    'detalles_liga':detalle.id,
                }) 

        #CARGAR DATOS DE IMPUESTOS
        c = connections[connection_name].cursor()
        c.execute('SELECT DOCTO_CM_ID, IMPUESTO_ID, COMPRA_NETA, OTROS_IMPUESTOS, PCTJE_IMPUESTO, IMPORTE_IMPUESTO FROM impuestos_doctos_cm where DOCTO_CM_ID=%s',[documento.id])
        impuestos = c.fetchall()
        compras_netas, otros_impuestos, porcentajes_impuestos, importes_impuesto, impuestos_ids = '', '', '', '', ''

        for impuesto in impuestos:
            compras_netas = "%s%s,"%(compras_netas, impuesto[2])
            otros_impuestos= "%s%s,"%(otros_impuestos, impuesto[3])
            porcentajes_impuestos = "%s%s,"%(porcentajes_impuestos, impuesto[4])
            importes_impuesto = "%s%s,"%(importes_impuesto, impuesto[5])
            impuestos_ids = "%s%s,"%(impuestos_ids, impuesto[1])
        
        initial_impuestos = {
                'compras_netas':compras_netas,
                'otros_impuestos':otros_impuestos,
                'porcentajes_impuestos':porcentajes_impuestos,
                'importes_impuesto':importes_impuesto,
                'impuestos_ids':impuestos_ids,
            }

        documento = DocumentoCompras()

    comprasdet_forms = DocumentoComprasDetalleFormset(DocumentoComprasDetalleManageForm, extra=1, can_delete=True)
    compradetalles_formset = comprasdet_forms(request.POST or None, instance=documento, initial = initial_formset)

    impuestos_form = DocumentoComprasImpuestosManageForm( request.POST or None, initial= initial_impuestos)

    documento_form = ComprasManageForm( request.POST or None, instance = documento, initial = initial_form)
    if documento_form.is_valid() and compradetalles_formset.is_valid() and impuestos_form.is_valid():
        documento = documento_form.save(commit=False)
        if not documento.id:
            documento.usuario_creador = request.user.username

        documento.usuario_ult_modif = request.user.username
        documento.tipo = 'C'
        documento.subtipo = 'N'
        documento.aplicado = 'N'
        documento.acreditar_cxp= 'N' 
        documento.contabilizado = 'N'
        documento.forma_emitida = 'N'
        
        importe_neto = 0
        for articulo_form in compradetalles_formset:
            importe_neto = importe_neto + articulo_form.cleaned_data['precio_total_neto']

        documento.importe_neto = importe_neto
        documento.save()
        documento_liga = None
        if type == 'O':
            documento_fte.estado = 'R'
            documento_fte.save()
            documento_liga = DocumentoComprasLiga.objects.create(
                    id=None,
                    documento_fte = documento_fte,
                    documento_dest = documento,
                )

            impuestos_ids =  impuestos_form.cleaned_data['impuestos_ids'].split(',')
            compras_netas =  impuestos_form.cleaned_data['compras_netas'].split(',')
            otros_impuestos =  impuestos_form.cleaned_data['otros_impuestos'].split(',')
            porcentajes_impuestos =  impuestos_form.cleaned_data['porcentajes_impuestos'].split(',')
            importes_impuesto = impuestos_form.cleaned_data['importes_impuesto'].split(',')

            #Guardar impuestos
            for impuesto_id, compra_neta, otro_impuestos, porcentaje_impuestos, importe_impuestos in zip(impuestos_ids, compras_netas, otros_impuestos, porcentajes_impuestos, importes_impuesto):
                if impuesto_id != "":
                    c = connections[connection_name].cursor()
                    query =  '''INSERT INTO "IMPUESTOS_DOCTOS_CM" ("DOCTO_CM_ID", "IMPUESTO_ID", "COMPRA_NETA", "OTROS_IMPUESTOS", "PCTJE_IMPUESTO", "IMPORTE_IMPUESTO") \
                        VALUES (%s, %s, %s, %s, %s, %s)'''
                    c.execute(query,[documento.id,  int(impuesto_id), Decimal(compra_neta),  Decimal(otro_impuestos), Decimal(porcentaje_impuestos), Decimal(importe_impuestos)])
                    c.close()

            plazos = CondicionPagoCPPlazo.objects.filter(condicion_de_pago=documento.condicion_pago)
            for plazo in plazos:
                fecha_vencimiento = documento.fecha + timedelta(days=plazo.dias)
                c = connections[connection_name].cursor()
                query =  '''INSERT INTO "VENCIMIENTOS_CARGOS_CM" ("DOCTO_CM_ID", "FECHA_VENCIMIENTO", "PCTJE_VEN") \
                    VALUES (%s, %s, %s)'''
                c.execute(query,[documento.id,  fecha_vencimiento, plazo.porcentaje_de_venta])
                c.close()


        #GUARDA ARTICULOS
        for articulo_form in compradetalles_formset:
            detalle = articulo_form.save(commit = False)
            #PARA CREAR UNO NUEVO

            if not detalle.id or (type == 'O' and initial_form['id'] == None):
                detalle.documento = documento

        compradetalles_formset.save()

        #CREAR LOS LIGAS DE LOS DETALLES
        for articulo_form in compradetalles_formset:
            detalle = articulo_form.save(commit = False)
            detalle_ligas = articulo_form.cleaned_data['detalles_liga'].split(',')
    
            for detalle_liga in detalle_ligas:
                if detalle_liga != [u'']:
                    detalle_doc = DocumentoComprasDetalle.objects.get(pk=detalle_liga)
                    con = connections[connection_name].cursor()
                    query =  '''INSERT INTO DOCTOS_CM_LIGAS_DET (DOCTO_CM_LIGA_ID, DOCTO_CM_DET_FTE_ID, DOCTO_CM_DET_DEST_ID) \
                        VALUES (%s, %s, %s)'''
                    con.execute(query,[documento_liga.id, detalle_doc.id , detalle.id])
                    con.close()

        compradetalles_formset.save()
        
        return HttpResponseRedirect('/compras/compras/')

    documentos_relacionados = DocumentoComprasLiga.objects.filter(documento_dest= documento)
    # vencimientos = VencimientoCargoCompra.objects.filter(documento=documento)
    
    c = {
        'documento_form':documento_form, 
        'formset':compradetalles_formset, 
        'documentos_relacionados':documentos_relacionados,
        'impuestos_form':impuestos_form,
        'message':message,
    }

    return render_to_response(template_name, c, context_instance=RequestContext(request))