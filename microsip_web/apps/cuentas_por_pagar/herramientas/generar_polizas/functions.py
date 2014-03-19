 #encoding:utf-8
from django.db.models import Sum
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist

#Modelos de modulos
from .models import *
def get_object_or_empty(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model()
        
def get_totales_documento_cp(cuenta_contado = None, documento=None, conceptos_poliza=None, totales_cuentas=None, msg='', error='',depto_co=None, connection_name = None):
    from microsip_web.libs.contabilidad import agregarTotales
    campos_particulares = get_object_or_empty(CuentasXPagarDocumentoCargoLibres, pk=documento.id)

    try:
        cuenta_proveedor =  ContabilidadCuentaContable.objects.get(cuenta=documento.proveedor.cuenta_xpagar).cuenta
    except ObjectDoesNotExist:
        cuenta_proveedor = None

    #Para saber si es contado o es credito
    if documento.naturaleza_concepto == 'C':
        try:
            es_contado = documento.condicion_pago == cuenta_contado
        except ObjectDoesNotExist:    
            es_contado = True
            error = 1
            msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% documento.folio
    else:
        es_contado = False

    if es_contado:
        condicion_pago_txt = 'contado'
    elif not es_contado:
        condicion_pago_txt = 'credito'

    importe         = 0
    total           = 0
    descuento       = 0

    impuestos = {
        'iva': {'contado':0,'credito':0,},
        'iva_retenido': 0,
        'isr_retenido':0,
    }
    
    importesDocto       = CuentasXPagarDocumentoImportes.objects.filter(docto_cp=documento, cancelado='N')
    for importeDocumento in importesDocto:
        impuestos['iva'][condicion_pago_txt] = impuestos['iva'][condicion_pago_txt] + (importeDocumento.total_impuestos)
        impuestos['iva_retenido']            = impuestos['iva_retenido'] + importeDocumento.iva_retenido
        impuestos['isr_retenido']            = impuestos['isr_retenido'] + importeDocumento.isr_retenido
        importe = importe + importeDocumento.importe
        descuento = descuento + importeDocumento.dscto_ppag

    total = total + impuestos['iva']['contado'] + impuestos['iva']['credito'] + importe - impuestos['iva_retenido'] - impuestos['isr_retenido']

    proveedores         = 0
    bancos              = 0
    compras_0           = 0
    compras_16          = 0
    compras_16_credito  = 0
    compras_0_credito   = 0
    compras_16_contado  = 0
    compras_0_contado   = 0

    if impuestos <= 0:
        compras_0 = importe
    else:
        compras_16 = importe

    #si llega a  haber un proveedor que no tenga cargar impuestos
    if compras_16 < 0:
        compras_0 += compras_16
        compras_16 = 0
        msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
        if crear_polizas_por == 'Dia':
            msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

        error = 1

    #Si es a credito
    if not es_contado:
        compras_16_credito  = compras_16
        compras_0_credito   = compras_0
        proveedores         = total - descuento
    elif es_contado:
        compras_16_contado  = compras_16
        compras_0_contado   = compras_0
        bancos              = total - descuento

    compras = {
        'iva_0':{'contado':compras_0_contado,'credito':compras_0_credito,},
        'iva'  :{'contado':compras_16_contado,'credito':compras_16_credito,},
    }

    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        compras             = compras,
        impuestos           = impuestos,
        proveedores         = proveedores,
        folio_documento     = documento.folio,
        bancos              = bancos,
        campos_particulares = campos_particulares,
        descuento           = descuento,
        depto_co            = depto_co,
        cuenta_proveedor    = cuenta_proveedor,
        error               = error,
        msg                 = msg,
    )

    return totales_cuentas, error, msg