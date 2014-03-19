 #encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections
from django.db.models import Sum
from decimal import *
import datetime, time

#Modelos de modulos 
from microsip_web.libs.api.models import *
from microsip_web.apps.ventas.models import *
from microsip_web.libs.contabilidad import agregarTotales as  agregarTotales2
#libs
from microsip_api.comun.sic_db import next_id

def get_descuento_total_ve(facturaID, connection_name = None):
    c = connections[connection_name].cursor()
    c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_VE(%s,'S') AS  A;"% facturaID)
    row = c.fetchone()
    return int(row[0])

def get_totales_documento_ve(cuenta_contado= None, documento= None, conceptos_poliza=None, totales_cuentas=None, msg='', error='', depto_co=None, connection_name =None):  
    #Si es una factura
    if documento.tipo == 'F':
        campos_particulares = VentasDocumentoFacturaLibres.objects.filter(pk=documento.id)[0]
    #Si es una devolucion
    elif documento.tipo == 'D':
        campos_particulares = VentasDocumentoFacturaDevLibres.objects.filter(pk=documento.id)[0]

    try:
        cuenta_cliente =  ContabilidadCuentaContable.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
    except ObjectDoesNotExist:
        cuenta_cliente = None
    
    total_impuestos     = documento.impuestos_total
    importe_neto        = documento.importe_neto
    total               = (total_impuestos + importe_neto)
    descuento           = get_descuento_total_ve(documento.id, connection_name)

    #Para saber si es contado o es credito
    try:
        es_contado = documento.condicion_pago == cuenta_contado
    except ObjectDoesNotExist:    
        es_contado = True
        error = 1
        msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% documento.folio
    
    clientes, bancos = 0, 0
    if es_contado:
        condicion_pago_txt = 'contado'
        bancos = total - descuento
    elif not es_contado:
        condicion_pago_txt = 'credito'
        clientes = total - descuento

    ventas = {
        'iva_0':{'contado':0,'credito':0,},
        'iva'  :{'contado':0,'credito':0,},
    }
    impuestos = {
        'iva': {'contado':0,'credito':0,},
        'ieps':{'contado':0,'credito':0,}
    }

    documento_impuestos = VentasDocumentoImpuesto.objects.filter(documento=documento).values_list('impuesto','importe','venta_neta','porcentaje')

    for documento_impuesto_list in documento_impuestos:
        documento_impuesto = {
            'tipo': Impuesto.objects.get(pk=documento_impuesto_list[0]).tipoImpuesto,
            'importe':documento_impuesto_list[1],
            'venta_neta':documento_impuesto_list[2],
            'porcentaje': documento_impuesto_list[3],
        }

        #Si es impuesto tipo IVA (16,15,etc.)
        if documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'V' and documento_impuesto['porcentaje'] > 0:
            ventas['iva'][condicion_pago_txt] = documento_impuesto['venta_neta']
            impuestos['iva'][condicion_pago_txt]  = documento_impuesto['importe']
        #Si es IVA al 0
        elif documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'V' and documento_impuesto['porcentaje'] == 0:
            ventas['iva_0'][condicion_pago_txt] = documento_impuesto['venta_neta']
        #Si es IEPS
        elif documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'P':
            impuestos['ieps'][condicion_pago_txt] = documento_impuesto['importe']
            
    #si llega a  haber un proveedor que no tenga cargar impuestos
    if ventas['iva']['contado'] < 0 or ventas['iva']['credito'] < 0:
        msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
        if crear_polizas_por == 'Dia':
            msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

        error = 1
    
    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        ventas              = ventas,
        impuestos           = impuestos,
        folio_documento     = documento.folio,
        descuento           = descuento,
        cliente_id          = documento.cliente.id,
        clientes            = clientes,
        cuenta_cliente      = cuenta_cliente,
        bancos              = bancos,
        campos_particulares = campos_particulares,
        depto_co            = depto_co,
        error               = error,
        msg                 = msg,
    )

    return totales_cuentas, error, msg