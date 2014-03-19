 #encoding:utf-8
from django.db.models import Sum
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
#Modelos de modulos
from .models import *
      
def get_totales_documento_cc(cuenta_contado = None, documento=None, conceptos_poliza=None, totales_cuentas=None, msg='', error='',depto_co=None, connection_name = None):
    from microsip_web.libs.contabilidad import agregarTotales
    
    try:
        cuenta_cliente =  ContabilidadCuentaContable.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
    except ObjectDoesNotExist:
        cuenta_cliente = None

    #Para saber si es contado o es credito
    campos_particulares = []
    if documento.naturaleza_concepto == 'C':
        try:
            es_contado = documento.condicion_pago == cuenta_contado
        except ObjectDoesNotExist:    
            es_contado = True
            error = 1
            msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% documento.folio

        try:
            campos_particulares = CuentasXCobrarDocumentoCargoLibres.objects.get(pk=documento.id)
        except ObjectDoesNotExist:
            campos_particulares =[]

    elif documento.naturaleza_concepto == 'R':
        es_contado = True
        try:
            campos_particulares = CuentasXCobrarDocumentoCreditoLibres.objects.get(pk=documento.id)
        except ObjectDoesNotExist:
            campos_particulares =[]

    if not campos_particulares == []:
        campos_particulares = campos_particulares

    importesDocto       = CuentasXCobrarDocumentoImportes.objects.filter(docto_cc=documento, cancelado='N')

    impuestos       = 0
    importe     = 0
    total           = 0
    iva_retenido    = 0
    isr_retenido = 0
    descuento           = 0

    for importeDocumento in importesDocto:
        impuestos       = impuestos + (importeDocumento.total_impuestos * documento.tipo_cambio)
        importe         = importe + (importeDocumento.importe * documento.tipo_cambio)
        iva_retenido    = iva_retenido + importeDocumento.iva_retenido
        isr_retenido    = isr_retenido + importeDocumento.isr_retenido
        descuento       = descuento + importeDocumento.dscto_ppag

    total               = total + impuestos + importe - iva_retenido - isr_retenido
    clientes            = 0
    bancos              = 0
    ventas_0            = 0
    ventas_16           = 0
    ventas_16_credito   = 0
    ventas_0_credito    = 0
    ventas_16_contado   = 0
    ventas_0_contado    = 0
    iva_efec_cobrado    = 0
    iva_pend_cobrar     = 0

    if impuestos <= 0:
        ventas_0 = importe
    else:
        ventas_16 = importe

    #si llega a  haber un proveedor que no tenga cargar impuestos
    if ventas_16 < 0:
        ventas_0 += ventas_16
        ventas_16 = 0
        msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
        if crear_polizas_por == 'Dia':
            msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

        error = 1

    #Si es a credito
    if not es_contado:
        ventas_16_credito   = ventas_16
        ventas_0_credito    = ventas_0
        iva_pend_cobrar     = impuestos
        clientes            = total - descuento
    elif es_contado:
        ventas_16_contado   = ventas_16
        ventas_0_contado    = ventas_0
        iva_efec_cobrado    = impuestos
        bancos              = total - descuento
    
    ventas = {
        'iva_0':{'contado':ventas_0_contado,'credito':ventas_0_credito,},
        'iva'  :{'contado':ventas_16_contado,'credito':ventas_16_credito,},
    }

    impuestos = {
        'iva': {'contado':iva_efec_cobrado,'credito':iva_pend_cobrar,},
        # 'ieps':{'contado':0,'credito':0,}
    }

    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        ventas              = ventas,
        impuestos           = impuestos,
        iva_retenido        = iva_retenido,
        isr_retenido        = isr_retenido,
        descuento           = descuento,
        clientes            = clientes,
        cuenta_cliente      = cuenta_cliente,
        bancos              = bancos,
        campos_particulares = campos_particulares,
        depto_co            = depto_co,
        error               = error,
        msg                 = msg,
    )


    return totales_cuentas, error, msg