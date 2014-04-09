#encoding:utf-8
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from .models import *
from microsip_api.comun.sic_db import get_conecctionname

@login_required(login_url='/login/')
def remisiones_view(request, template_name='ventas/documentos/remisiones_crear_cargos/remisiones.html'):
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

from django.core import serializers
import json

class generar_cargosbyremisionesview(TemplateView):
    ''' Genera un cargo en cuentas por pagar de las remisiones dadas.'''

    def get(self, request, *args, **kwargs):
        errors, remisiones_cargadas = [], []

        ids = request.GET['ids']
        ids = map(int, ids[:len(ids)-1].split(','))
        documentos = VentasDocumento.objects.filter(pk__in=ids, cargo_generado=None)

        for documento in documentos:
            cxc_documento = CuentasXCobrarDocumento.objects.create(
                concepto = CuentasXCobrarConcepto.objects.get(id_interno='F'),
                fecha =  documento.fecha,
                cliente = documento.cliente,
                tipo_cambio = documento.tipo_cambio,
                condicion_pago = documento.condicion_pago,
            )

            CuentasXCobrarDocumentoImportes.objects.create(
                docto_cc = cxc_documento,
                importe = documento.importe_total,
                total_impuestos = documento.impuestos_total,
                iva_retenido =0,
                isr_retenido =0,
                dscto_ppag=0,
            )

            remisiones_cargadas.append(documento.id)
            documento.cargo_generado = True
            documento.save(update_fields=('cargo_generado',))
        data = {
            'remisiones_cargadas': remisiones_cargadas,
            'errors': errors,
        }
        data = json.dumps(data)
        return HttpResponse(data, mimetype='application/json')
# Create your views here.
