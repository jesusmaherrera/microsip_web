 #encoding:utf-8
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.db.models import Sum, Max
from decimal import *
from django.db import connections
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime, time

#Modelos de modulos 
from microsip_web.libs.api.models import *
from microsip_web.apps.contabilidad.models import *
from microsip_web.apps.cuentas_por_pagar.models import *
from microsip_web.apps.cuentas_por_cobrar.models import *
from microsip_web.apps.ventas.models import *
from microsip_web.apps.punto_de_venta.models import *

#libs
from custom_db.main import next_id

def agregarTotales(totales_cuentas, connection_name = "", **kwargs):

    #Valores cuentas por pagar
    compras_16_credito  = kwargs.get('compras_16_credito', 0)
    compras_0_credito   = kwargs.get('compras_0_credito', 0)
    compras_0_contado   = kwargs.get('compras_0_contado', 0)
    compras_16_contado  = kwargs.get('compras_16_contado', 0)
    folio_documento = kwargs.get('folio_documento', 0)
    iva_contado     = kwargs.get('iva_contado', 0)
    iva_credito     = kwargs.get('iva_credito', 0)
    iva_retenido    = kwargs.get('iva_retenido', 0)
    isr_retenido    = kwargs.get('isr_retenido', 0)
    proveedores     = kwargs.get('proveedores', 0)
    cuenta_proveedor    = kwargs.get('cuenta_proveedor', None)
    
    #valores ventas
    ventas_16_credito   = kwargs.get('ventas_16_credito', 0)
    ventas_0_credito    = kwargs.get('ventas_0_credito', 0)
    ventas_0_contado    = kwargs.get('ventas_0_contado', 0)
    ventas_16_contado   = kwargs.get('ventas_16_contado', 0)

    cliente_id  = kwargs.get('cliente_id', 0)
    clientes    = kwargs.get('clientes', 0)
    cuenta_cliente  = kwargs.get('cuenta_cliente', None)

    #Valores generales
    descuento   = kwargs.get('descuento', 0)
    bancos      = kwargs.get('bancos', 0)
    
    depto_co            = kwargs.get('depto_co', None)
    conceptos_poliza    = kwargs.get('conceptos_poliza', [])
    campos_particulares = kwargs.get('campos_particulares', None)

    error = kwargs.get('error', 0)
    msg = kwargs.get('msg', '')
    impuestos_documento = kwargs.get('impuestos_documento', [])

    asientos_a_ingorar = []
    valores_extra = {}
    valor_extra = 0
    for concepto in conceptos_poliza:
        if concepto.valor_tipo == 'Segmento_1' and not campos_particulares.segmento_1 == None and campos_particulares.segmento_1 != '':
            asientos_a_ingorar.append(concepto.asiento_ingora)
        if concepto.valor_tipo == 'Segmento_2' and not campos_particulares.segmento_2 == None and campos_particulares.segmento_2 != '':
            asientos_a_ingorar.append(concepto.asiento_ingora)
        if concepto.valor_tipo == 'Segmento_3' and not campos_particulares.segmento_3 == None and campos_particulares.segmento_3 != '':
            asientos_a_ingorar.append(concepto.asiento_ingora)
        if concepto.valor_tipo == 'Segmento_4' and not campos_particulares.segmento_4 == None and campos_particulares.segmento_4 != '':
            asientos_a_ingorar.append(concepto.asiento_ingora)
        if concepto.valor_tipo == 'Segmento_5' and not campos_particulares.segmento_5 == None and campos_particulares.segmento_5 != '':
            asientos_a_ingorar.append(concepto.asiento_ingora)

        #Para sumar o restar dos asientos
        if not concepto.asiento_ingora == None and not concepto.asiento_ingora == '' :
            if not concepto.asiento_ingora[0].isdigit() and (concepto.asiento_ingora[0]=='+' or concepto.asiento_ingora[0]=='-'):
                if concepto.asiento_ingora[1:].isdigit():
                    asientos_a_ingorar.append(concepto.posicion)

                    if concepto.valor_tipo == 'Proveedores':
                        valor_extra  = proveedores
                    elif concepto.valor_tipo == 'Bancos':
                        valor_extra  = bancos
                    elif concepto.valor_tipo == 'Clientes':
                        valor_extra  = clientes
                    elif concepto.valor_tipo == 'Descuentos':
                        valor_extra  = descuento
                    elif concepto.valor_tipo == 'IVA Retenido':
                        valor_extra  = iva_retenido
                    elif concepto.valor_tipo == 'IVA':
                        if concepto.valor_contado_credito == 'Credito':
                            valor_extra  = iva_credito
                        elif concepto.valor_contado_credito == 'Contado':
                            valor_extra  = iva_contado
                        elif concepto.valor_contado_credito == 'Ambos':
                            valor_extra  = iva_credito + iva_contado
                    elif concepto.valor_tipo == 'ISR Retenido':
                        valor_extra = isr_retenido
                    elif concepto.valor_tipo == 'Compras':
                        if concepto.valor_contado_credito == 'Credito':
                            if concepto.valor_iva == '0':
                                valor_extra = compras_0_credito
                            elif concepto.valor_iva == 'I':
                                valor_extra = compras_16_credito
                            elif concepto.valor_iva == 'A':
                                valor_extra = compras_0_credito + compras_16_credito
                        elif concepto.valor_contado_credito == 'Contado':
                            if concepto.valor_iva == '0':
                                valor_extra = compras_0_contado
                            elif concepto.valor_iva == 'I':
                                valor_extra = compras_16_contado
                            elif concepto.valor_iva == 'A':
                                valor_extra = compras_0_contado + compras_16_contado
                        elif concepto.valor_contado_credito == 'Ambos':
                            if concepto.valor_iva == '0':
                                valor_extra = compras_0_credito + compras_0_contado
                            elif concepto.valor_iva == 'I':
                                valor_extra = compras_16_credito + compras_16_contado
                            elif concepto.valor_iva == 'A':
                                valor_extra = compras_0_credito + compras_0_contado + compras_16_credito + compras_16_contado
                    elif concepto.valor_tipo == 'Ventas':
                        if concepto.valor_contado_credito == 'Credito':
                            if concepto.valor_iva == '0':
                                valor_extra = ventas_0_credito
                            elif concepto.valor_iva == 'I':
                                valor_extra = ventas_16_credito
                            elif concepto.valor_iva == 'A':
                                valor_extra = ventas_0_credito + ventas_16_credito
                        elif concepto.valor_contado_credito == 'Contado':
                            if concepto.valor_iva == '0':
                                valor_extra = ventas_0_contado
                            elif concepto.valor_iva == 'I':
                                valor_extra = ventas_16_contado
                            elif concepto.valor_iva == 'A':
                                valor_extra = ventas_0_contado + ventas_16_contado
                        elif concepto.valor_contado_credito == 'Ambos':
                            if concepto.valor_iva == '0':
                                valor_extra = ventas_0_credito + ventas_0_contado
                            elif concepto.valor_iva == 'I':
                                valor_extra = ventas_16_credito + ventas_16_contado
                            elif concepto.valor_iva == 'A':
                                valor_extra = ventas_0_credito + ventas_0_contado + ventas_16_credito + ventas_16_contado

                if concepto.asiento_ingora[0]=='-':
                    valor_extra = -valor_extra

                if valores_extra.has_key(concepto.asiento_ingora[1:]):
                    valores_extra[concepto.asiento_ingora[1:]] = valores_extra[concepto.asiento_ingora[1:]] + valor_extra
                else:
                    valores_extra[concepto.asiento_ingora[1:]] = valor_extra
                
    for concepto in conceptos_poliza:
        importe = 0
        cuenta  = []
        clave_cuenta_tipoAsiento = []
        if concepto.valor_tipo == 'Segmento_1' and not campos_particulares.segmento_1 == None and campos_particulares.segmento_1 != '':
            totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_1, totales_cuentas, depto_co, concepto.tipo, error, msg, folio_documento, concepto.asiento_ingora, connection_name)
        elif concepto.valor_tipo == 'Segmento_2' and not campos_particulares.segmento_2 == None and campos_particulares.segmento_2 != '': 
            totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_2, totales_cuentas, depto_co, concepto.tipo, error, msg, folio_documento, concepto.asiento_ingora, connection_name)
        elif concepto.valor_tipo == 'Segmento_3' and not campos_particulares.segmento_3 == None and campos_particulares.segmento_3 != '': 
            totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_3, totales_cuentas, depto_co, concepto.tipo, error, msg, folio_documento, concepto.asiento_ingora, connection_name)
        elif concepto.valor_tipo == 'Segmento_4' and not campos_particulares.segmento_4 == None and campos_particulares.segmento_4 != '':
            totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_4, totales_cuentas, depto_co, concepto.tipo, error, msg, folio_documento, concepto.asiento_ingora, connection_name)
        elif concepto.valor_tipo == 'Segmento_5' and not campos_particulares.segmento_5 == None and campos_particulares.segmento_5 != '': 
            totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_5, totales_cuentas, depto_co, concepto.tipo, error, msg, folio_documento, concepto.asiento_ingora, connection_name)
        elif concepto.valor_tipo == 'Compras' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_contado_credito == 'Credito':
                if concepto.valor_iva == '0':
                    importe = compras_0_credito
                elif concepto.valor_iva == 'I':
                    importe = compras_16_credito
                elif concepto.valor_iva == 'A':
                    importe = compras_0_credito + compras_16_credito
            elif concepto.valor_contado_credito == 'Contado':
                if concepto.valor_iva == '0':
                    importe = compras_0_contado
                elif concepto.valor_iva == 'I':
                    importe = compras_16_contado
                elif concepto.valor_iva == 'A':
                    importe = compras_0_contado + compras_16_contado
            elif concepto.valor_contado_credito == 'Ambos':
                if concepto.valor_iva == '0':
                    importe = compras_0_credito + compras_0_contado
                elif concepto.valor_iva == 'I':
                    importe = compras_16_credito + compras_16_contado
                elif concepto.valor_iva == 'A':
                    importe = compras_0_credito + compras_0_contado + compras_16_credito + compras_16_contado
            cuenta  = concepto.cuenta_co.cuenta
        elif concepto.valor_tipo == 'Ventas' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_contado_credito == 'Credito':
                if concepto.valor_iva == '0':
                    importe = ventas_0_credito
                elif concepto.valor_iva == 'I':
                    importe = ventas_16_credito
                elif concepto.valor_iva == 'A':
                    importe = ventas_0_credito + ventas_16_credito
            elif concepto.valor_contado_credito == 'Contado':
                if concepto.valor_iva == '0':
                    importe = ventas_0_contado
                elif concepto.valor_iva == 'I':
                    importe = ventas_16_contado
                elif concepto.valor_iva == 'A':
                    importe = ventas_0_contado + ventas_16_contado
            elif concepto.valor_contado_credito == 'Ambos':
                if concepto.valor_iva == '0':
                    importe = ventas_0_credito + ventas_0_contado
                elif concepto.valor_iva == 'I':
                    importe = ventas_16_credito + ventas_16_contado
                elif concepto.valor_iva == 'A':
                    importe = ventas_0_credito + ventas_0_contado + ventas_16_credito + ventas_16_contado

            campo_cuenta = clientes_config_cuenta.objects.filter(valor_contado_credito= concepto.valor_contado_credito, valor_iva= concepto.valor_iva)

            if campo_cuenta.count() > 0:

                cuenta_temp = getattr(libresClientes.objects.get(id=cliente_id), campo_cuenta[0].campo_cliente) 
                if cuenta_temp != '' and cuenta_temp != 0 and cuenta_temp != None:
                    if CuentaCo.objects.filter(cuenta=cuenta_temp).exists():
                        cuenta = cuenta_temp
                    else:
                        cliente_nombre = Cliente.objects.filter(id=cliente_id)
                        msg = 'existe almenos una cuenta INVALIDA en el cliente %s. Corrigela para continuar'% cliente_nombre
                        error = 2
                        cuenta  = concepto.cuenta_co.cuenta        
                else:
                    cuenta  = concepto.cuenta_co.cuenta    
            else:
                cuenta  = concepto.cuenta_co.cuenta
            
        elif concepto.valor_tipo == 'IVA' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_contado_credito == 'Credito':
                importe = iva_credito
            elif concepto.valor_contado_credito == 'Contado':
                importe = iva_contado
            elif concepto.valor_contado_credito == 'Ambos':
                importe = iva_credito + iva_contado

            cuenta = concepto.cuenta_co.cuenta
        elif concepto.valor_tipo == 'IVA Retenido' and not concepto.posicion in asientos_a_ingorar:
            importe = iva_retenido
            cuenta = concepto.cuenta_co.cuenta
        elif concepto.valor_tipo == 'ISR Retenido' and not concepto.posicion in asientos_a_ingorar:
            importe = isr_retenido
            cuenta = concepto.cuenta_co.cuenta
        elif concepto.valor_tipo == 'Proveedores' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_iva == 'A':
                importe = proveedores

            if cuenta_proveedor == None:
                cuenta = concepto.cuenta_co.cuenta
            else:
                cuenta = cuenta_proveedor
        elif concepto.valor_tipo == 'Clientes' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_iva == 'A':
                importe = clientes

            if cuenta_cliente == None:
                cuenta = concepto.cuenta_co.cuenta
            else:
                cuenta = cuenta_cliente
        elif concepto.valor_tipo == 'Bancos' and not concepto.posicion in asientos_a_ingorar:
            if concepto.valor_iva == 'A':
                importe =   bancos

            cuenta = concepto.cuenta_co.cuenta
        elif concepto.valor_tipo == 'Descuentos' and not concepto.posicion in asientos_a_ingorar:
            importe = descuento
            cuenta = concepto.cuenta_co.cuenta
        
        if concepto.posicion in valores_extra:
            importe = importe + valores_extra[concepto.posicion]

        posicion_cuenta_depto_tipoAsiento = "%s+%s/%s:%s"% (concepto.posicion, cuenta, depto_co, concepto.tipo)
        importe = importe

        #Se es tipo segmento pone variables en cero para que no se calculen otra ves valores por ya estan calculados
        if concepto.valor_tipo == 'Segmento_1' or concepto.valor_tipo == 'Segmento_2' or concepto.valor_tipo == 'Segmento_3' or concepto.valor_tipo == 'Segmento_4' or concepto.valor_tipo == 'Segmento_5':
            importe = 0

        if not posicion_cuenta_depto_tipoAsiento == [] and importe > 0:
            if posicion_cuenta_depto_tipoAsiento in totales_cuentas:
                totales_cuentas[posicion_cuenta_depto_tipoAsiento] = [totales_cuentas[posicion_cuenta_depto_tipoAsiento][0] + Decimal(importe),int(concepto.posicion)]
            else:
                totales_cuentas[posicion_cuenta_depto_tipoAsiento]  = [Decimal(importe),int(concepto.posicion)]

    return totales_cuentas, error, msg

def new_folio_poliza(tipo_poliza, fecha = None, connection_name = None):
    """ Generar un folio nuevo de una poliza e incrementa el consecutivo de folios """
    prefijo = tipo_poliza.prefijo
    if not tipo_poliza.prefijo:
        prefijo = ''

    try:
        if tipo_poliza.tipo_consec == 'M':
            tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, mes=fecha.month, ano = fecha.year)
        elif tipo_poliza.tipo_consec == 'E':
            tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, ano=fecha.year, mes=0)
        elif tipo_poliza.tipo_consec == 'P':
            tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, mes=0, ano =0)
    except ObjectDoesNotExist:
        if tipo_poliza.tipo_consec == 'M':      
            tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', connection_name), tipo_poliza=tipo_poliza, ano=fecha.year, mes=fecha.month, consecutivo = 1,)
        elif tipo_poliza.tipo_consec == 'E':
            #Si existe permanente toma su consecutivo para crear uno nuevo si no existe inicia en 1
            consecutivo = TipoPolizaDetalle.objects.filter(tipo_poliza = tipo_poliza, mes=0, ano =0).aggregate(max = Sum('consecutivo'))['max']

            if consecutivo == None:
                consecutivo = 1

            tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', connection_name), tipo_poliza=tipo_poliza, ano=fecha.year, mes=0, consecutivo=consecutivo,)
        elif tipo_poliza.tipo_consec == 'P':
            consecutivo = TipoPolizaDetalle.objects.all().aggregate(max = Sum('consecutivo'))['max']

            if consecutivo == None:
                consecutivo = 1

            tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', connection_name), tipo_poliza=tipo_poliza, ano=0, mes=0, consecutivo = consecutivo,)                                
    
    

    folio = '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]) 

    #CONSECUTIVO DE FOLIO DE POLIZA
    tipo_poliza_det.consecutivo += 1 
    tipo_poliza_det.save()
    
    return folio

def get_object_or_empty(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model()

def get_descuento_total_ve(facturaID, connection_name = None):
    c = connections[connection_name].cursor()
    c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_VE(%s,'S') AS  A;"% facturaID)
    row = c.fetchone()
    return int(row[0])

def get_descuento_total_pv(documentoId, connection_name = None):
    c = connections[connection_name].cursor()
    c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_PV(%s,'','',0) AS  A;"% documentoId)
    row = c.fetchone()
    return int(row[0])

def get_totales_cuentas_by_segmento(segmento='',totales_cuentas=[], depto_co=None, concepto_tipo=None, error=0, msg='', documento_folio='', asiento_ingora=0, connection_name=None):
    importe = 0
    if asiento_ingora=='':
        asiento_ingora = 0
        
    cuenta  = []
    clave_cuenta_tipoAsiento = []

    segmento = segmento.split(',')
    
    if not segmento == []:
        for importe_segmento in segmento:

            cuenta_cantidad     = importe_segmento.split('=')
            cuenta_depto= cuenta_cantidad[0].split("/")
            
            try:
                cuenta      =  CuentaCo.objects.get(cuenta=cuenta_depto[0]).cuenta
            except ObjectDoesNotExist:
                error = 2
                msg = 'NO EXISTE O ES INCORRECTA almenos una [CUENTA CONTABLE] indicada en un segmento en el documento con folio[%s], Corrigelo para continuar'% documento_folio
            
            
            if len(cuenta_depto) == 2:
                try:
                    depto_co = ContabilidadDepartamento.objects.get(clave=cuenta_depto[1]).clave
                except ObjectDoesNotExist:
                    error = 2
                    msg = 'NO EXISTE almenos un [DEPARTEMENTO CONTABLE] indicado en un segmento en el documento con folio [%s], Corrigelo para continuar'% documento_folio
            
            try:
                importe = float(cuenta_cantidad[1])
            except:
                error = 3
                msg = 'Cantidad incorrecta en un segmento en el documento [%s], Corrigelo para continuar'% documento_folio

            if error == 0:
                posicion_cuenta_depto_tipoAsiento = "%s+%s/%s:%s"% (asiento_ingora, cuenta, depto_co, concepto_tipo)
                importe = importe

                if not posicion_cuenta_depto_tipoAsiento == [] and importe > 0:
                    if posicion_cuenta_depto_tipoAsiento in totales_cuentas:
                        totales_cuentas[posicion_cuenta_depto_tipoAsiento] = [totales_cuentas[posicion_cuenta_depto_tipoAsiento][0] + Decimal(importe),int(asiento_ingora)]
                    else:
                        totales_cuentas[posicion_cuenta_depto_tipoAsiento]  = [Decimal(importe),int(asiento_ingora)]

    return totales_cuentas, error, msg

##########################################
##                                      ##
##           Totales documentos         ##
##                                      ##
##########################################

def get_totales_documento_cc(cuenta_contado = None, documento=None, conceptos_poliza=None, totales_cuentas=None, msg='', error='',depto_co=None, connection_name = None):
    
    try:
        cuenta_cliente =  CuentaCo.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
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
    
    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        ventas_0_credito    = ventas_0_credito,
        ventas_16_credito   = ventas_16_credito,
        ventas_0_contado    = ventas_0_contado,
        ventas_16_contado   = ventas_16_contado,
        iva_contado         = iva_efec_cobrado,
        iva_credito         = iva_pend_cobrar,
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

def get_totales_documento_cp(cuenta_contado = None, documento=None, conceptos_poliza=None, totales_cuentas=None, msg='', error='',depto_co=None, connection_name = None):
    campos_particulares = get_object_or_empty(CuentasXPagarDocumentoCargoLibres, pk=documento.id)

    try:
        cuenta_proveedor =  CuentaCo.objects.get(cuenta=documento.proveedor.cuenta_xpagar).cuenta
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

    importesDocto       = CuentasXPagarDocumentoImportes.objects.filter(docto_cp=documento, cancelado='N')
    
    impuestos       = 0
    importe         = 0
    total           = 0
    iva_retenido    = 0
    isr_retenido    = 0
    descuento       = 0

    for importeDocumento in importesDocto:
        impuestos           = impuestos + (importeDocumento.total_impuestos * documento.tipo_cambio)
        importe             = importe + (importeDocumento.importe * documento.tipo_cambio)
        iva_retenido        = iva_retenido + importeDocumento.iva_retenido
        isr_retenido        = isr_retenido + importeDocumento.isr_retenido
        descuento           = descuento + importeDocumento.dscto_ppag

    total               = total + impuestos + importe - iva_retenido - isr_retenido

    proveedores         = 0
    bancos              = 0
    compras_0           = 0
    compras_16          = 0
    compras_16_credito  = 0
    compras_0_credito   = 0
    compras_16_contado  = 0
    compras_0_contado   = 0
    iva_pend_pagar      = 0
    iva_efec_pagado     = 0

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
        iva_pend_pagar      = impuestos
        proveedores         = total - descuento
    elif es_contado:
        compras_16_contado  = compras_16
        compras_0_contado   = compras_0
        iva_efec_pagado     = impuestos
        bancos              = total - descuento

    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        compras_16_credito  = compras_16_credito,
        compras_0_credito   = compras_0_credito,
        iva_credito         = iva_pend_pagar,
        proveedores         = proveedores,
        compras_16_contado  = compras_16_contado,
        folio_documento     = documento.folio,
        compras_0_contado   = compras_0_contado,
        iva_contado         = iva_efec_pagado,
        bancos              = bancos,
        iva_retenido        = iva_retenido,
        isr_retenido        = isr_retenido,
        campos_particulares = campos_particulares,
        descuento           = descuento,
        depto_co            = depto_co,
        cuenta_proveedor    = cuenta_proveedor,
        error               = error,
        msg                 = msg,
    )

    return totales_cuentas, error, msg

def get_totales_documento_ve(cuenta_contado= None, documento= None, conceptos_poliza=None, totales_cuentas=None, msg='', error='', depto_co=None, connection_name =None):  
    #Si es una factura
    if documento.tipo == 'F':
        campos_particulares = VentasDocumentoFacturaLibres.objects.filter(pk=documento.id)[0]
    #Si es una devolucion
    elif documento.tipo == 'D':
        campos_particulares = VentasDocumentoFacturaDevLibres.objects.filter(pk=documento.id)[0]

    try:
        cuenta_cliente =  CuentaCo.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
    except ObjectDoesNotExist:
        cuenta_cliente = None

    #Para saber si es contado o es credito
    try:
        es_contado = documento.condicion_pago == cuenta_contado
    except ObjectDoesNotExist:    
        es_contado = True
        error = 1
        msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% documento.folio
    
    impuestos           = documento.total_impuestos * documento.tipo_cambio
    importe_neto        = documento.importe_neto * documento.tipo_cambio
    total               = (impuestos + importe_neto) * documento.tipo_cambio
    descuento           = get_descuento_total_ve(documento.id, connection_name) * documento.tipo_cambio
    clientes            = 0
    bancos              = 0
    iva_efec_cobrado    = 0
    iva_pend_cobrar     = 0
    ventas_16_credito   = 0
    ventas_16_contado   = 0
    ventas_0_credito    = 0
    ventas_0_contado    = 0

    ventas_0            = VentasDocumentoDetalle.objects.filter(docto_ve= documento).extra(
            tables =['impuestos_articulos', 'impuestos'],
            where =
            [
                "impuestos_articulos.ARTICULO_ID = doctos_ve_det.ARTICULO_ID",
                "impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
                "impuestos.PCTJE_IMPUESTO = 0 ",
            ],
        ).aggregate(ventas_0 = Sum('precio_total_neto'))['ventas_0']
    
    if ventas_0 == None:
        ventas_0 = 0 
    documento_tipo_cambio = documento.tipo_cambio
    ventas_0 = ventas_0 * documento.tipo_cambio
    ventas_16 = total - ventas_0 - impuestos

    #si llega a  haber un proveedor que no tenga cargar impuestos
    if ventas_16 < 0:
        ventas_0 += ventas_16
        ventas_16 = 0
        msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
        if crear_polizas_por == 'Dia':
            msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

        error = 1

    #SI LA FACTURA ES A CREDITO
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

    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        ventas_0_credito    = ventas_0_credito,
        ventas_16_credito   = ventas_16_credito,
        ventas_0_contado    = ventas_0_contado,
        ventas_16_contado   = ventas_16_contado,
        iva_contado         = iva_efec_cobrado,
        iva_credito         = iva_pend_cobrar,
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

def get_impuestos_documento(documento, connection_name):
    """ Para obtener impuestos de un documento determinado """
    documento_tipo = documento.__class__.__name__
    c = connections[connection_name].cursor()
    if documento_tipo == 'Docto_PV':
        consulta ="SELECT IMPUESTO_ID, IMPORTE_IMPUESTO FROM IMPUESTOS_DOCTOS_PV WHERE DOCTO_PV_ID= %s"% documento.id
    elif documento_tipo == 'VentasDocumento':
        consulta ="SELECT IMPUESTO_ID, IMPORTE_IMPUESTO FROM IMPUESTOS_DOCTOS_VE WHERE DOCTO_VE_ID= %s"% documento.id
    elif documento_tipo == 'DoctosCm':
        consulta ="SELECT IMPUESTO_ID, IMPORTE_IMPUESTO FROM IMPUESTOS_DOCTOS_CM WHERE DOCTO_CM_ID= %s"% documento.id
    c.execute(consulta)
    impuestos = c.fetchall()
    c.close()
    return impuestos


def get_totales_documento_pv(cuenta_contado = None, documento = None, conceptos_poliza = None, totales_cuentas = None, msg = '', error='', depto_co = None, connection_name = None):  
    """ Obtiene los totales de un documento indicado para posteriormente crear las polizas """
    
    es_contado = False
    try:
        cuenta_cliente =  CuentaCo.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
    except ObjectDoesNotExist:
        cuenta_cliente = None 

    #Para saber si es contado o es credito
    total_credito = Docto_pv_cobro.objects.filter(documento_pv=documento, forma_cobro__tipo='R').aggregate(total_credito = Sum('importe'))['total_credito']
    if total_credito == None:
        total_credito = 0
        es_contado = True

    impuestos           = documento.total_impuestos * documento.tipo_cambio
    importe_neto        = documento.importe_neto * documento.tipo_cambio
    total               = impuestos + importe_neto
    descuento           = get_descuento_total_pv(documento.id, connection_name) * documento.tipo_cambio
    clientes            = 0
    bancos              = 0
    iva_efec_cobrado    = 0
    iva_pend_cobrar     = 0
    ventas_16_credito   = 0
    ventas_16_contado   = 0
    ventas_0_credito    = 0
    ventas_0_contado    = 0

    ventas_0            = Docto_pv_det.objects.filter(documento_pv= documento).extra(
            tables =['impuestos_articulos', 'impuestos'],
            where =
            [
                "impuestos_articulos.ARTICULO_ID = doctos_pv_det.ARTICULO_ID",
                "impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
                "impuestos.PCTJE_IMPUESTO = 0 ",
            ],
        ).aggregate(ventas_0 = Sum('precio_total_neto'))['ventas_0']
    
    impuestos_documento = Impuestos_docto_pv.objects.filter(documento_pv=documento)
    
    if ventas_0 == None:
        ventas_0 = 0 

    ventas_0 = ventas_0 * documento.tipo_cambio

    ventas_16 = total - ventas_0 - impuestos

    #si llega a  haber un proveedor que no tenga cargar impuestos
    if ventas_16 < 0:
        ventas_0 += ventas_16
        ventas_16 = 0
        msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
        if crear_polizas_por == 'Dia':
            msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

        error = 1

    #SI LA FACTURA ES A CREDITO
    if not es_contado:
        ventas_16_credito   = ventas_16
        ventas_0_credito    = ventas_0
        iva_pend_cobrar     = impuestos
        clientes            = total_credito
        #bancos                 = total - total_credito
    elif es_contado:
        ventas_16_contado   = ventas_16
        ventas_0_contado    = ventas_0
        iva_efec_cobrado    = impuestos
        bancos              = total

    totales_cuentas, error, msg = agregarTotales(
        connection_name     = connection_name,
        conceptos_poliza    = conceptos_poliza,
        totales_cuentas     = totales_cuentas, 
        ventas_0_credito    = ventas_0_credito,
        ventas_16_credito   = ventas_16_credito,
        ventas_0_contado    = ventas_0_contado,
        ventas_16_contado   = ventas_16_contado,
        iva_contado         = iva_efec_cobrado,
        iva_credito         = iva_pend_cobrar,
        descuento           = descuento,
        clientes            = clientes,
        cuenta_cliente      = cuenta_cliente,
        bancos              = bancos,
        depto_co            = depto_co,
        error               = error,
        msg                 = msg,
        impuestos_documento = impuestos_documento,
    )
    
    return totales_cuentas, error, msg

def crear_polizas(origen_documentos, documentos, depto_co, informacion_contable, plantilla=None, crear_polizas_por='',crear_polizas_de=None, connection_name = None, usuario_micorsip='',**kwargs):
    """ Crea las polizas contables segun el tipo y origen de documentos que se mande """
    
    msg             = kwargs.get('msg', '')
    descripcion     = kwargs.get('descripcion', '')
    tipo_documento  = kwargs.get('tipo_documento', '')
    
    conceptos_poliza = []
    error = 0
    DocumentosData      = []
    cuenta              = ''
    importe = 0
    
    if origen_documentos == 'cuentas_por_cobrar':
        conceptos_poliza    = DetallePlantillaPolizas_CC.objects.filter(plantilla_poliza_CC=plantilla).order_by('posicion')
    elif origen_documentos == 'cuentas_por_pagar':
        conceptos_poliza    = DetallePlantillaPolizas_CP.objects.filter(plantilla_poliza_CP=plantilla).order_by('posicion')
    elif origen_documentos == 'ventas':
        conceptos_poliza    = DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla).order_by('posicion')
    elif origen_documentos == 'punto_de_venta':
        conceptos_poliza    = DetallePlantillaPolizas_pv.objects.filter(plantilla_poliza_pv=plantilla).order_by('posicion')
    
    moneda_local        = Moneda.objects.get(es_moneda_local='S')
    documento_numero    = 0
    polizas             = []
    detalles_polizas    = []
    totales_cuentas     = {}
    
    for documento_no, documento in enumerate(documentos):
        #es_contado = documento.condicion_pago == informacion_contable.condicion_pago_contado
        descripcion_extra   = ''

        siguente_documento = documentos[(documento_no +1)%len(documentos)]
        documento_numero = documento_no
        if origen_documentos == 'cuentas_por_cobrar':
            totales_cuentas, error, msg = get_totales_documento_cc(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co, connection_name)
        elif origen_documentos == 'cuentas_por_pagar':
            descripcion_extra = documento.proveedor.nombre

            totales_cuentas, error, msg = get_totales_documento_cp(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co, connection_name)
        elif origen_documentos == 'ventas':
            totales_cuentas, error, msg = get_totales_documento_ve(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co, connection_name)
        elif origen_documentos == 'punto_de_venta':
            totales_cuentas, error, msg = get_totales_documento_pv(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co, connection_name)
        
        if error == 0:
            #Cuando la fecha de la documento siguiente sea diferente y sea por DIA, o sea la ultima
            if (not documento.fecha == siguente_documento.fecha and crear_polizas_por == 'Dia') or documento_no +1 == len(documentos) or crear_polizas_por == 'Documento':

                #tipo_poliza
                if origen_documentos == 'ventas':
                    if  tipo_documento == 'F':
                        tipo_poliza = informacion_contable.tipo_poliza_ve
                    elif tipo_documento == 'D': 
                        tipo_poliza = informacion_contable.tipo_poliza_dev
                elif origen_documentos == 'cuentas_por_cobrar' or origen_documentos == 'cuentas_por_pagar':
                    tipo_poliza = TipoPoliza.objects.filter(clave=documento.concepto.clave_tipo_poliza)[0]
                elif origen_documentos == 'punto_de_venta':
                    if  tipo_documento == 'V':
                        tipo_poliza = TipoPoliza.objects.get(clave=Registry.objects.get(nombre='TIPO_POLIZA_VENTAS_PV').valor) 
                    elif tipo_documento == 'D':
                        tipo_poliza = TipoPoliza.objects.get(clave=Registry.objects.get(nombre='TIPO_POLIZA_DEVOL_PV').valor)
                        #form_reg.fields['tipo_poliza_cobros_cc'].initial = Registry.objects.get(nombre='TIPO_POLIZA_COBROS_CXC_PV').valor

                #Si no tiene una descripcion el documento se pone lo que esta indicado en la descripcion general
                descripcion_doc = "(%s) %s"% (descripcion_extra, documento.descripcion)
                
                if documento.descripcion == None or crear_polizas_por=='Dia' or crear_polizas_por == 'Periodo':
                    descripcion_doc = descripcion

                referencia = documento.folio
                if crear_polizas_por == 'Dia':
                    referencia = ''

                poliza = ContabilidadDocumento(
                        id                      = next_id('ID_DOCTOS', connection_name),
                        tipo_poliza             = tipo_poliza,
                        fecha                   = documento.fecha,
                        moneda                  = moneda_local, 
                        tipo_cambio             = 1,
                        estatus                 = 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
                        descripcion             = descripcion_doc,
                        forma_emitida           = 'N', sistema_origen = 'CO',
                        nombre                  = '',
                        grupo_poliza_periodo    = None,
                        integ_ba                = 'N',
                        usuario_creador         = usuario_micorsip,
                        fechahora_creacion      = datetime.now(), usuario_aut_creacion = None, 
                        usuario_ult_modif       = usuario_micorsip, fechahora_ult_modif = datetime.now(), usuario_aut_modif    = None,
                        usuario_cancelacion     = None, fechahora_cancelacion   =  None, usuario_aut_cancelacion                = None,
                    )
                
                polizas.append(poliza)
                #GUARDA LA PILIZA
                #poliza_o = poliza.save()

                posicion = 1
                totales_cuentas = totales_cuentas.items()

                totales_cuentas.sort()

                for posicion_cuenta_depto_tipoAsiento, importe in totales_cuentas:
                    cuenta_deptotipoAsiento = posicion_cuenta_depto_tipoAsiento.split('+')[1].split('/')
                    cuenta_co = CuentaCo.objects.get(cuenta=cuenta_deptotipoAsiento[0])
                    depto_tipoAsiento = cuenta_deptotipoAsiento[1].split(':')
                    depto_co = ContabilidadDepartamento.objects.get(clave=depto_tipoAsiento[0])
                    tipo_asiento = depto_tipoAsiento[1]
                    
                    detalle_poliza = ContabilidadDocumentoDetalle(
                        id              = -1,
                        docto_co        = poliza,
                        cuenta          = cuenta_co,
                        depto_co        = depto_co,
                        tipo_asiento    = tipo_asiento,
                        importe         = importe[0],
                        importe_mn      = 0,#PENDIENTE
                        ref             = referencia,
                        descripcion     = '',
                        posicion        = posicion,
                        recordatorio    = None,
                        fecha           = documento.fecha,
                        cancelado       = 'N', aplicado = 'N', ajuste = 'N', 
                        moneda          = moneda_local,
                    )

                    posicion +=1
                    detalles_polizas.append(detalle_poliza)

                #DE NUEVO CONVIERTO LA VARIABLE A DICCIONARIO
                totales_cuentas = {}
            
            documento.contabilizado ='S'
            documento.save(update_fields=['contabilizado'])
    if error == 0:
        for poliza in polizas:
            poliza.poliza = new_folio_poliza(poliza.tipo_poliza, poliza.fecha, connection_name)
            DocumentosData.append({
                'folio':poliza.poliza,
                })

        ContabilidadDocumento.objects.bulk_create(polizas)
        ContabilidadDocumentoDetalle.objects.bulk_create(detalles_polizas)
    else:
        DocumentosData = []

    polizas = []
    detalles_polizas = []
    return msg, DocumentosData