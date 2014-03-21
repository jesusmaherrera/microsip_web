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
from microsip_web.apps.cuentas_por_pagar.herramientas.generar_polizas.models import *
from microsip_web.apps.cuentas_por_cobrar.herramientas.generar_polizas.models import *
from microsip_web.apps.ventas.herramientas.generar_polizas.models import *
from microsip_web.apps.punto_de_venta.models import *

from microsip_api.comun.sic_db import next_id

class TotalesCuentas(dict):
    def __init__(self, conceptos_poliza):
        ''' conceptos_poliza: son los conceptos que llevan las polizas. '''
        self.error = None
        self.msg = ''
        self.conceptos_poliza = conceptos_poliza
   
    def get_valortotales_by_concepto(self, totales, valor_contado_credito, valor_iva):
        #totales de credito
        if valor_contado_credito == 'Credito':
            if valor_iva == '0':
                return totales['iva_0']['credito']
            elif valor_iva == 'I':
                return totales['iva']['credito']
            elif valor_iva == 'A':
                return totales['iva_0']['credito'] + totales['iva']['credito']
        #totales de contado
        elif valor_contado_credito == 'Contado':
            if valor_iva == '0':
                return totales['iva_0']['contado']
            elif valor_iva == 'I':
                return totales['iva']['contado']
            elif valor_iva == 'A':
                return totales['iva_0']['contado'] + totales['iva']['contado'] 
        #totales de contado y credito
        elif valor_contado_credito == 'Ambos':
            if valor_iva == '0':
                return totales['iva_0']['contado'] + totales['iva_0']['credito']
            elif valor_iva == 'I':
                return totales['iva']['contado'] + totales['iva']['credito']
            elif valor_iva == 'A':
                contado = totales['iva_0']['contado'] + totales['iva']['contado'] 
                credito = totales['iva_0']['credito'] + totales['iva']['credito']
                return contado + credito
        return None

    def agregar_totalesbysegmento(self, documento_folio, segmento, depto_co, concepto_tipo, asiento_ingora=0):
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
                    cuenta      =  ContabilidadCuentaContable.objects.get(cuenta=cuenta_depto[0]).cuenta
                except ObjectDoesNotExist:
                    self.error = 2
                    self.msg = 'NO EXISTE O ES INCORRECTA almenos una [CUENTA CONTABLE] indicada en un segmento en el documento con folio[%s], Corrigelo para continuar'% documento_folio
                
                
                if len(cuenta_depto) == 2:
                    try:
                        depto_co = ContabilidadDepartamento.objects.get(clave=cuenta_depto[1]).clave
                    except ObjectDoesNotExist:
                        self.error = 2
                        self.msg = 'NO EXISTE almenos un [DEPARTEMENTO CONTABLE] indicado en un segmento en el documento con folio [%s], Corrigelo para continuar'% documento_folio
                
                try:
                    importe = float(cuenta_cantidad[1])
                except:
                    self.error = 3
                    self.msg = 'Cantidad incorrecta en un segmento en el documento [%s], Corrigelo para continuar'% documento_folio

                if self.error == 0:
                    asiento_id = "%s+%s/%s:%s"% (asiento_ingora, cuenta, depto_co, concepto_tipo)
                    #Si hay algo por agregar
                    if not asiento_id == [] and importe > 0:
                        if asiento_id in self:
                            self[asiento_id] = {
                                'tipo_asiento':concepto.tipo,
                                'departamento':depto_co.clave,
                                'cuenta':cuenta,
                                'importe':self[asiento_id]['importe'] + Decimal(importe),
                            }
                        else:
                            self[asiento_id]  = {
                                'tipo_asiento':concepto.tipo,
                                'departamento':depto_co.clave,
                                'cuenta':cuenta,
                                'importe':Decimal(importe),
                            }

        return self.error, self.msg

    def agregar_valorcuenta(self, kwargs):
        #Valores cuentas por pagar
        folio_documento = kwargs.get('folio_documento', 0)
        compras  = kwargs.get('compras', 0)
        ventas = kwargs.get('ventas',None)
        error  = kwargs.get('error', 0)
        msg = kwargs.get('msg',None)
        impuestos = kwargs.get('impuestos', None)
        
        proveedores     = kwargs.get('proveedores', 0)
        cuenta_proveedor    = kwargs.get('cuenta_proveedor', None)
        
        cliente_id  = kwargs.get('cliente_id', 0)
        clientes    = kwargs.get('clientes', 0)
        cuenta_cliente  = kwargs.get('cuenta_cliente', None)

        #Valores generales
        descuento   = kwargs.get('descuento', 0)
        bancos      = kwargs.get('bancos', 0)
        
        depto_co            = kwargs.get('depto_co', None)
        campos_particulares = kwargs.get('campos_particulares', None)
        impuestos_documento = kwargs.get('impuestos_documento', [])
        
        asientos_a_ingorar = []
        valores_extra = {}
        valor_extra = 0
        for concepto in self.conceptos_poliza:
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
                            valor_extra  = impuestos['iva_retenido']
                        elif concepto.valor_tipo == 'IEPS':
                            if concepto.valor_contado_credito == 'Credito':
                                valor_extra  = impuestos['ieps']['credito']
                            elif concepto.valor_contado_credito == 'Contado':
                                valor_extra  = impuestos['ieps']['contado']
                            elif concepto.valor_contado_credito == 'Ambos':
                                valor_extra  = impuestos['ieps']['credito'] + impuestos['ieps']['contado']
                        elif concepto.valor_tipo == 'IVA':
                            if concepto.valor_contado_credito == 'Credito':
                                valor_extra  = impuestos['iva']['credito']
                            elif concepto.valor_contado_credito == 'Contado':
                                valor_extra  = impuestos['iva']['contado']
                            elif concepto.valor_contado_credito == 'Ambos':
                                valor_extra  = impuestos['iva']['contado'] + impuestos['iva']['credito']
                        elif concepto.valor_tipo == 'ISR Retenido':
                            valor_extra = impuestos['isr_retenido']
                        elif concepto.valor_tipo == 'Compras':
                             valor_extra = self.get_valortotales_by_concepto(
                                    totales = compras,
                                    valor_contado_credito = concepto.valor_contado_credito,
                                    valor_iva   = concepto.valor_iva
                                )
                        elif concepto.valor_tipo == 'Ventas':
                            valor_extra = self.get_valortotales_by_concepto(
                                    totales = ventas,
                                    valor_contado_credito = concepto.valor_contado_credito,
                                    valor_iva   = concepto.valor_iva
                                )
                    if concepto.asiento_ingora[0]=='-':
                        valor_extra = -valor_extra

                    if valores_extra.has_key(concepto.asiento_ingora[1:]):
                        valores_extra[concepto.asiento_ingora[1:]] = valores_extra[concepto.asiento_ingora[1:]] + valor_extra
                    else:
                        valores_extra[concepto.asiento_ingora[1:]] = valor_extra
                    
        for concepto in self.conceptos_poliza:
            importe = 0
            cuenta  = []
            clave_cuenta_tipoAsiento = []
            
            if concepto.valor_tipo == 'Segmento_1' or concepto.valor_tipo == 'Segmento_2' or concepto.valor_tipo == 'Segmento_3' or concepto.valor_tipo == 'Segmento_4' or concepto.valor_tipo == 'Segmento_5':
                segmento = None
                if concepto.valor_tipo == 'Segmento_1' and campos_particulares.segmento_1 != None and campos_particulares.segmento_1 != '':
                    segmento =  campos_particulares.segmento_1
                elif concepto.valor_tipo == 'Segmento_2' and campos_particulares.segmento_2 != None and campos_particulares.segmento_1 != '': 
                    segmento =  campos_particulares.segmento_2
                elif concepto.valor_tipo == 'Segmento_3' and campos_particulares.segmento_3 != None and campos_particulares.segmento_1 != '': 
                    segmento =  campos_particulares.segmento_3
                elif concepto.valor_tipo == 'Segmento_4' and campos_particulares.segmento_4 != None and campos_particulares.segmento_1 != '':
                    segmento =  campos_particulares.segmento_4
                elif concepto.valor_tipo == 'Segmento_5' and campos_particulares.segmento_5 != None and campos_particulares.segmento_1 != '': 
                    segmento =  campos_particulares.segmento_5    
                
                if segmento:
                    self.error, self.msg = self.agregar_totalesbysegmento(folio_documento, segmento, depto_co, concepto.tipo, concepto.asiento_ingora)
            elif concepto.valor_tipo == 'Compras' and not concepto.posicion in asientos_a_ingorar:
                importe = self.get_valortotales_by_concepto(
                       totales = compras,
                       valor_contado_credito = concepto.valor_contado_credito,
                       valor_iva   = concepto.valor_iva
                   )
                cuenta  = concepto.cuenta_co.cuenta
            elif concepto.valor_tipo == 'Ventas' and not concepto.posicion in asientos_a_ingorar:
                importe = self.get_valortotales_by_concepto(
                    totales = ventas,
                    valor_contado_credito = concepto.valor_contado_credito,
                    valor_iva   = concepto.valor_iva
                )

                campo_cuenta = clientes_config_cuenta.objects.filter(valor_contado_credito= concepto.valor_contado_credito, valor_iva= concepto.valor_iva)

                if campo_cuenta.count() > 0:

                    cuenta_temp = getattr(libresClientes.objects.get(id=cliente_id), campo_cuenta[0].campo_cliente) 
                    if cuenta_temp != '' and cuenta_temp != 0 and cuenta_temp != None:
                        if ContabilidadCuentaContable.objects.filter(cuenta=cuenta_temp).exists():
                            cuenta = cuenta_temp
                        else:
                            cliente_nombre = Cliente.objects.filter(id=cliente_id)
                            self.msg = 'existe almenos una cuenta INVALIDA en el cliente %s. Corrigela para continuar'% cliente_nombre
                            self.error = 2
                            cuenta  = concepto.cuenta_co.cuenta        
                    else:
                        cuenta  = concepto.cuenta_co.cuenta    
                else:
                    cuenta  = concepto.cuenta_co.cuenta
                
            elif concepto.valor_tipo == 'IVA' and not concepto.posicion in asientos_a_ingorar:
                if concepto.valor_contado_credito == 'Credito':
                    importe = impuestos['iva']['credito']
                elif concepto.valor_contado_credito == 'Contado':
                    importe = impuestos['iva']['contado']
                elif concepto.valor_contado_credito == 'Ambos':
                    importe = impuestos['iva']['contado'] + impuestos['iva']['credito']

                cuenta = concepto.cuenta_co.cuenta
            elif concepto.valor_tipo == 'IEPS' and not concepto.posicion in asientos_a_ingorar:
                if concepto.valor_contado_credito == 'Credito':
                    importe = impuestos['ieps']['credito']
                elif concepto.valor_contado_credito == 'Contado':
                    importe = impuestos['ieps']['contado']
                elif concepto.valor_contado_credito == 'Ambos':
                    importe = impuestos['ieps']['credito'] + impuestos['ieps']['contado']

                cuenta = concepto.cuenta_co.cuenta
            elif concepto.valor_tipo == 'IVA Retenido' and not concepto.posicion in asientos_a_ingorar:
                importe = impuestos['iva_retenido']
                cuenta = concepto.cuenta_co.cuenta
            elif concepto.valor_tipo == 'ISR Retenido' and not concepto.posicion in asientos_a_ingorar:
                importe = impuestos['isr_retenido']
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

            #Se es tipo segmento pone variables en cero para que no se calculen otra ves valores por ya estan calculados
            if concepto.valor_tipo == 'Segmento_1' or concepto.valor_tipo == 'Segmento_2' or concepto.valor_tipo == 'Segmento_3' or concepto.valor_tipo == 'Segmento_4' or concepto.valor_tipo == 'Segmento_5':
                importe = 0

            asiento_id = "%s+%s/%s:%s"% (concepto.posicion, cuenta, depto_co, concepto.tipo)
            
            #Si hay algo por agregar
            if not asiento_id == [] and importe > 0:
                if asiento_id in self:
                    self[asiento_id] = {
                        'tipo_asiento':concepto.tipo,
                        'departamento':depto_co.clave,
                        'cuenta':cuenta,
                        'importe':self[asiento_id]['importe'] + Decimal(importe),
                    }
                else:
                    self[asiento_id]  = {
                        'tipo_asiento':concepto.tipo,
                        'departamento':depto_co.clave,
                        'cuenta':cuenta,
                        'importe':Decimal(importe),
                    }
        return self.error, self.msg

def get_descuento_total_pv(documentoId, connection_name = None):
    c = connections[connection_name].cursor()
    c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_PV(%s,'','',0) AS  A;"% documentoId)
    row = c.fetchone()
    return int(row[0])

##########################################
##                                      ##
##           Totales documentos         ##
##                                      ##
##########################################

def get_totales_documento_pv(cuenta_contado = None, documento = None, conceptos_poliza = None, totales_cuentas = None, msg = '', error='', depto_co = None, connection_name = None):  
    """ Obtiene los totales de un documento indicado para posteriormente crear las polizas """
    
    es_contado = False
    try:
        cuenta_cliente =  ContabilidadCuentaContable.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
    except ObjectDoesNotExist:
        cuenta_cliente = None 

    #Para saber si es contado o es credito
    total_credito = PuntoVentaCobro.objects.filter(documento_pv=documento, forma_cobro__tipo='R').aggregate(total_credito = Sum('importe'))['total_credito']
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

    ventas_0            = PuntoVentaDocumentoDetalle.objects.filter(documento_pv= documento).extra(
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
    moneda = moneda_local
    tipo_cambio = 1

    totales_cuentas = TotalesCuentas(conceptos_poliza)

    for documento_no, documento in enumerate(documentos):
        #es_contado = documento.condicion_pago == informacion_contable.condicion_pago_contado

        #Descripcion extra
        descripcion_extra   = ''
        if origen_documentos == 'cuentas_por_pagar':
            descripcion_extra = documento.proveedor.nombre
        elif origen_documentos == 'ventas':
            descripcion_extra = documento.folio

        siguente_documento = documentos[(documento_no +1)%len(documentos)]
        documento_numero = documento_no
        
        kwargs_totales, error, msg = documento.get_totales(informacion_contable.condicion_pago_contado)
        kwargs_totales['depto_co'] = depto_co
        if documento.id == 17834:
            objects.asd
        totales_cuentas.agregar_valorcuenta(kwargs_totales)

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
                if documento.descripcion:
                    descripcion = documento.descripcion
                descripcion_doc = "(%s) %s"% (descripcion_extra, descripcion)

                referencia = documento.folio
                if crear_polizas_por == 'Dia':
                    referencia = ''
                if crear_polizas_por == 'Documento':
                    if origen_documentos == 'cuentas_por_pagar':
                        moneda = documento.proveedor.moneda
                    elif origen_documentos == 'cuentas_por_cobrar':
                        moneda = documento.cliente.moneda
                    else:                        
                        moneda = documento.moneda
                    tipo_cambio = documento.tipo_cambio

                poliza = ContabilidadDocumento(
                        id                      = next_id('ID_DOCTOS', connection_name),
                        tipo_poliza             = tipo_poliza,
                        fecha                   = documento.fecha,
                        moneda                  = moneda, 
                        tipo_cambio             = tipo_cambio,
                        estatus                 = 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
                        descripcion             = descripcion_doc,
                        forma_emitida           = 'N', sistema_origen = 'CO',
                        nombre                  = '',
                        grupo_poliza_periodo    = None,
                        integ_ba                = 'N',
                        usuario_creador         = usuario_micorsip,
                        fechahora_creacion      = datetime.datetime.now(), usuario_aut_creacion = None, 
                        usuario_ult_modif       = usuario_micorsip, fechahora_ult_modif = datetime.datetime.now(), usuario_aut_modif    = None,
                        usuario_cancelacion     = None, fechahora_cancelacion   =  None, usuario_aut_cancelacion                = None,
                    )
                
                polizas.append(poliza)
                #GUARDA LA PILIZA
                #poliza_o = poliza.save()
                for asiento in totales_cuentas.itervalues():
                    cuenta_co = ContabilidadCuentaContable.objects.get(cuenta=asiento['cuenta'])
                    depto_co = ContabilidadDepartamento.objects.get(clave= asiento['departamento'])

                    detalle_poliza = ContabilidadDocumentoDetalle(
                        id              = -1,
                        docto_co        = poliza,
                        cuenta          = cuenta_co,
                        depto_co        = depto_co,
                        tipo_asiento    = asiento['tipo_asiento'],
                        importe         = asiento['importe'],
                        importe_mn      = 0,#PENDIENTE
                        ref             = referencia,
                        descripcion     = '',
                        posicion        = -1,
                        recordatorio    = None,
                        fecha           = documento.fecha,
                        cancelado       = 'N', aplicado = 'N', ajuste = 'N', 
                        moneda          = moneda,
                    )

                    detalles_polizas.append(detalle_poliza)

                #DE NUEVO CONVIERTO LA VARIABLE A DICCIONARIO
                totales_cuentas.clear()
            
            documento.contabilizado ='S'
            documento.save(update_fields=['contabilizado'])
            
    if error == 0:
        for poliza in polizas:
            poliza.poliza = poliza.next_folio(using=connection_name)
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