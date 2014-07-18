#encoding:utf-8
from django.db import models
from django.db import router
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session
from microsip_api.comun.sic_db import next_id, first_or_none
import django.dispatch

from microsip_web.settings.local_settings import MICROSIP_MODULES
from django.db import connections

from microsip_api.models_base.comun.articulos import *
from microsip_api.models_base.comun.catalogos import *
from microsip_api.models_base.comun.clientes import *
from microsip_api.models_base.comun.listas import *
from microsip_api.models_base.comun.otros import *
from microsip_api.models_base.comun.proveedores import *

from microsip_api.models_base.configuracion.folios_fiscales import *
from microsip_api.models_base.configuracion.preferencias import *

from microsip_api.models_base.punto_de_venta.documentos import *
from microsip_api.models_base.punto_de_venta.listas import *

from microsip_api.models_base.compras.documentos import *
from microsip_api.models_base.compras.otros import *

from microsip_api.models_base.cuentas_por_pagar.documentos import *
from microsip_api.models_base.cuentas_por_pagar.catalogos import *

from microsip_api.models_base.cuentas_por_cobrar.documentos import *
from microsip_api.models_base.cuentas_por_cobrar.catalogos import *

from microsip_api.models_base.ventas.documentos import *

from microsip_api.models_base.inventarios.documentos import *
from microsip_api.models_base.inventarios.otros import *
from microsip_api.models_base.inventarios.catalogos import *

from microsip_api.models_base.contabilidad.documentos import *
from microsip_api.models_base.contabilidad.catalogos import *
from microsip_api.models_base.contabilidad.listas import *

from microsip_api.comun.comun_functions import split_letranumero

################################################################
####                                                        ####
####                      MODELOS OTROS                     ####
####                                                        ####
################################################################
def get_object_or_empty(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model()


class Carpeta(models.Model):
    nombre  = models.CharField(max_length=30)
    carpeta_padre = models.ForeignKey('self', related_name='carpeta_padre_a', blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.nombre

    class Meta:
        db_table = u'sic_carpeta'

################################################################
####                                                        ####
####                        OTROS                           ####
####                                                        ####
################################################################

@receiver(post_save)
def clear_cache(sender, **kwargs):
    if sender != Session:
        cache.clear()

class ConexionDB(models.Model):  
    nombre = models.CharField(max_length=100)
    TIPOS = (('L', 'Local'),('R', 'Remota'),)
    tipo = models.CharField(max_length=1, choices=TIPOS)
    servidor = models.CharField(max_length=250)
    carpeta_datos = models.CharField(max_length=300)
    usuario = models.CharField(max_length=300)
    password = models.CharField(max_length=300)

    def __str__(self):  
          return self.nombre    
          
    class Meta:
        app_label =u'auth' 

class AplicationPlugin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        app_label =u'auth'
        db_table = u'sic_aplicationplugin'

################################################################
####                                                        ####
####                        CONFIGURACION                   ####
####                                                        ####
################################################################

# PREFERENCIAS

class Registry(RegistryBase):
    pass

#FOLIOS FISCALES

class ConfiguracionFolioFiscal(ConfiguracionFolioFiscalBase): 
    pass

class ConfiguracionFolioFiscalUso(ConfiguracionFolioFiscalUsoBase):
    pass

################################################################
####                                                        ####
####                        COMUN                           ####
####                                                        ####
################################################################

class Pais(PaisBase):
    def save(self, *args, **kwargs):    
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        super(self.__class__, self).save(*args, **kwargs)
        
        if self.es_predet == 'S':
            Pais.objects.using(kwargs['using']).all().exclude(pk=self.id).update(es_predet='N')


class Estado(EstadoBase):
    def save(self, *args, **kwargs):
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        super(self.__class__, self).save(*args, **kwargs)
        
        if self.es_predet == 'S':
            Estado.objects.using(kwargs['using']).all().exclude(pk=self.id).update(es_predet='N')


class Ciudad(CiudadBase):
    def save(self, *args, **kwargs):
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        super(self.__class__, self).save(*args, **kwargs)

        if self.es_predet == 'S':
            Ciudad.objects.using(kwargs['using']).all().exclude(pk=self.id).update(es_predet='N')

class Moneda(MonedaBase):
    pass

class TipoCambio(TipoCambioBase):
    pass

class ViaEmbarque(ViaEmbarqueBase):
   pass

class FolioVenta(FolioVentaBase):
    pass

class FolioCompra(FolioCompraBase):
    pass

# ARTICULOS

class GrupoLineas(GrupoLineasBase):
    pass

class LineaArticulos(LineaArticulosBase):
    pass

class Articulo(ArticuloBase):
    if 'microsip_web.apps.main.comun.articulos.articulos.alertas' in MICROSIP_MODULES:
        UNIDADES_MEDIDA = ( ( 'N', 'No aplica' ),( 'D', 'Dias' ),( 'K', 'Kilometros' ), )
        alerta_unidades = models.IntegerField(default = 0, blank = True, null = True, db_column = 'SIC_ALERTA_UNIDADES' )
        alerta_unidad_medida = models.CharField( default = 'N', max_length = 1, choices = UNIDADES_MEDIDA, db_column = 'SIC_ALERTA_UNIDAD_MEDIDA' )
        
        # carpeta = models.ForeignKey( Carpeta, blank = True, null = True, db_column = 'SIC_CARPETA_ID' )
    
class ArticuloClaveRol(ArticuloClaveRolBase):
    pass

class ArticuloClave(ArticuloClaveBase):
    pass

class ArticuloPrecio(ArticuloPrecioBase):
    pass

class Almacen(AlmacenBase):
    inventariando = models.BooleanField(default= False, db_column = 'SIC_INVENTARIANDO' )
    inventario_conajustes = models.BooleanField(default= False, db_column = 'SIC_INVCONAJUSTES' )
    inventario_modifcostos = models.BooleanField(default= False, db_column = 'SIC_INVMODIFCOSTOS' )
    
class PrecioEmpresa(PrecioEmpresaBase):
    pass

class ArticuloDiscreto(ArticuloDiscretoBase):
    pass

class ArticuloDiscretoExistencia(ArticuloDiscretoExistenciaBase):
    pass

#CATALOGOS

class Banco(BancoBase):
    pass

# LISTAS

class ImpuestoTipo(ImpuestoTipoBase):
    pass

class Impuesto(ImpuestoBase):
    def save(self, *args, **kwargs):    
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        super(self.__class__, self).save(*args, **kwargs)

        if self.es_predet == 'S':
            Impuesto.objects.using(kwargs['using']).all().exclude(pk=self.id).update(es_predet='N')


class ImpuestosArticulo(ImpuestoArticuloBase):
    pass    

class Vendedor(VendedorBase):
    pass

# CLIENTES
class ClienteTipo(ClienteTipoBase):
    pass

class CondicionPago(CondicionPagoBase):
    def save(self, *args, **kwargs):    
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        super(self.__class__, self).save(*args, **kwargs)

        if self.es_predet == 'S':
            CondicionPago.objects.using(kwargs['using']).all().exclude(pk=self.id).update(es_predet='N')


class CondicionPagoPlazo(CondicionPagoPlazoBase):
    pass

class Cliente(ClienteBase):
    pass
        

class ClienteClaveRol(ClienteClaveRolBase):
    pass

class ClienteClave(ClienteClaveBase):
    pass

class ClienteDireccion(ClienteDireccionBase):
    pass

class libresClientes(libreClienteBase):
    if 'microsip_web.apps.ventas.herramientas.generar_polizas' or  'microsip_web.apps.ventas.herramientas' in MICROSIP_MODULES:
        cuenta_1 = models.CharField(max_length=99, db_column='CUENTA_1')
        cuenta_2 = models.CharField(max_length=99, db_column='CUENTA_2')
        cuenta_3 = models.CharField(max_length=99, db_column='CUENTA_3')
        cuenta_4 = models.CharField(max_length=99, db_column='CUENTA_4')
        cuenta_5 = models.CharField(max_length=99, db_column='CUENTA_5')

# PROVEEDORES

class ProveedorTipo(ProveedorTipoBase):
    pass
        
class Proveedor(ProveedorBase):
    pass

################################################################
####                                                        ####
####                      MODELOS OTROS                     ####
####                                                        ####
################################################################

class ArticuloCompatibleArticulo(models.Model):
    articulo = models.ForeignKey(Articulo, related_name="articulo_id_ca", blank=True, null=True)
    articulo_compatible = models.ForeignKey(Articulo, related_name="articulo_compatible_id_ca", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.articulo_compatible

    class Meta:
        db_table = u'sic_articulocomp_art'

class ArticuloCompatibleCarpeta(models.Model):
    articulo = models.ForeignKey(Articulo, related_name="articulo_id_cc", blank=True, null=True)
    carpeta_compatible = models.ForeignKey(Carpeta, related_name="carpeta_compatible_id_cc", blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.carpeta_compatible

    class Meta:
        db_table = u'sic_articulocomp_carp'

################################################################
####                                                        ####
####                      COMPRAS                           ####
####                                                        ####
################################################################

# OTROS

class Aduana(AduanaBase):
    pass

class Pedimento(PedimentoBase):
    pass

# DOCUMENTOS

class ComprasConsignatario(ComprasConsignatarioBase):
    pass

class ComprasDocumento(ComprasDocumentoBase):
    def next_folio( self, connection_name=None, **kwargs ):
        ''' Funcion para generar el siguiente folio de un documento de ventas '''

        #Parametros opcionales
        serie = kwargs.get('serie', None)
        consecutivos_folios = FolioCompra.objects.using(connection_name).filter(tipo_doc = self.tipo)
        if serie:
            consecutivos_folios = consecutivos_folios.filter(serie=serie)

        consecutivo_row = first_or_none(consecutivos_folios)
        consecutivo = ''
        if consecutivo_row:
            consecutivo = consecutivo_row.consecutivo 
            serie = consecutivo_row.serie
            if serie == u'@':
                serie = ''
                
        folio = '%s%s'% (serie,("%09d" % int(consecutivo))[len(serie):]) 

        consecutivo_row.consecutivo = consecutivo_row.consecutivo + 1
        consecutivo_row.save()

        return folio

    def save(self, *args, **kwargs):
        if self.folio == '':
            kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
            self.folio = self.next_folio(connection_name=kwargs['using'])

        super(self.__class__, self).save(*args, **kwargs)

class ComprasDocumentoCargoVencimiento(ComprasDocumentoCargoVencimientoBase):
    pass

class ComprasDocumentoDetalle(ComprasDocumentoDetalleBase):
    pass

class ComprasDocumentoImpuesto(ComprasDocumentoImpuestoBase):
   pass

class ComprasDocumentoLiga(ComprasDocumentoLigaBase):
    pass

class ComprasDocumentoLigaDetalle(ComprasDocumentoLigaDetalleBase):
    pass

#####################################################
##
##                         INVENTARIOS
##
##
#####################################################

# CATALOGOS

class InventariosConcepto(InventariosConceptoBase):
    pass

class InventariosCentroCostos(InventariosCentroCostosBase):
   pass

#  DOCUMENTOS

class InventariosDocumento(InventariosDocumentoBase):

    def next_folio( self, connection_name=None):
        ''' Funcion para generar el siguiente folio de un documento inventario '''

        folio = ''
        concepto_in = self.concepto
        if concepto_in.folio_autom and concepto_in.sig_folio:
            folio = "%09d" % int(concepto_in.sig_folio)
        concepto_in.sig_folio = "%09d" % (int(concepto_in.sig_folio)+1)
        concepto_in.save()

        return folio

    def save(self, *args, **kwargs):
        if not self.folio and self.concepto.folio_autom == 'S':
            kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
            self.folio = self.next_folio()

        super(self.__class__, self).save(*args, **kwargs)

class InventariosDocumentoDetalle(InventariosDocumentoDetalleBase):
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='SIC_FECHAHORA_U')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='SIC_USUARIO_ULT_MODIF')
    detalle_modificacionestime = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLETIME_MODIFICACIONES')
    
class InventariosDocumentoIF(InventariosDocumentoIFBase):
    pass

class InventariosDocumentoIFDetalle(InventariosDocumentoIFDetalleBase):
    pass

# OTROS

class InventariosDesgloseEnDiscretos(InventariosDesgloseEnDiscretosBase):
    pass

class InventariosDesgloseEnDiscretosIF(InventariosDesgloseEnDiscretosIFBase):
    pass


################################################################
####                                                        ####
####               MODELOS CUENTAS POR PAGAR                ####
####                                                        ####
################################################################

# CATALOGOS

class CuentasXPagarConcepto(CuentasXPagarConceptoBase):
    pass

class CuentasXPagarCondicionPago(CuentasXPagarCondicionPagoBase):
    pass

class CuentasXPagarCondicionPagoPlazoBase(CuentasXPagarCondicionPagoPlazoBase):
    pass

# DOCUMENTOS

class CuentasXPagarDocumento(CuentasXPagarDocumentoBase):

    def get_totales(self, cuenta_contado = None):
        ''' Para obtener totales de documento'''
        error = 0
        msg = ''
        
        campos_particulares = get_object_or_empty(CuentasXPagarDocumentoCargoLibres, pk=self.id)
        try:
            cuenta_contable =  ContabilidadCuentaContable.objects.get(cuenta=self.proveedor.cuenta_xpagar).cuenta
        except ObjectDoesNotExist:
            cuenta_contable = None

        #Para saber si es contado o es credito
        if self.naturaleza_concepto == 'C':
            try:
                es_contado = self.condicion_pago == cuenta_contado
            except ObjectDoesNotExist:    
                es_contado = True
                error = 1
                msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% self.folio
        else:
            es_contado = False

        if es_contado:
            condicion_pago_txt = 'contado'
        elif not es_contado:
            condicion_pago_txt = 'credito'

        importe         = 0
        descuento       = 0

        impuestos_desglosado = {
            'iva': {'contado':0,'credito':0,},
            'iva_retenido': 0,
            'isr_retenido':0,
        }

        importe_neto_desglosado = {
            'iva_0':{'contado':0,'credito':0,},
            'iva'  :{'contado':0,'credito':0,},
        }
        
        importesDocto = CuentasXPagarDocumentoImportes.objects.filter(docto_cp=self, cancelado='N')
        for importeDocumento in importesDocto:
            impuestos_desglosado['iva'][condicion_pago_txt] = impuestos_desglosado['iva'][condicion_pago_txt] + (importeDocumento.total_impuestos)
            impuestos_desglosado['iva_retenido']            = impuestos_desglosado['iva_retenido'] + importeDocumento.iva_retenido
            impuestos_desglosado['isr_retenido']            = impuestos_desglosado['isr_retenido'] + importeDocumento.isr_retenido
            importe = importe + importeDocumento.importe
            descuento = descuento + importeDocumento.dscto_ppag
        
        if impuestos_desglosado['iva'][condicion_pago_txt] > 0:
            importe_neto_desglosado['iva'][condicion_pago_txt] = importe
        else:
            importe_neto_desglosado['iva_0'][condicion_pago_txt] = importe

        #si llega a  haber un proveedor que no tenga cargar impuestos
        if importe_neto_desglosado['iva'][condicion_pago_txt] < 0:
            importe_neto_desglosado['iva_0'][condicion_pago_txt] += importe_neto_desglosado['iva'][condicion_pago_txt]
            importe_neto_desglosado['iva'][condicion_pago_txt] = 0
            msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
            if crear_polizas_por == 'Dia':
                msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

            error = 1

        totales = {
            'a_nombre_de': {
                'tipo':'proveedor',
                'id':None,
                'cuenta_contable':cuenta_contable,
            },
            'movimiento':'entrada',
            'folio':self.folio,
            'condicion_pago': condicion_pago_txt,
            'retenciones_total': impuestos_desglosado['iva_retenido'] + impuestos_desglosado['isr_retenido'],
            'importe_neto':{
                'total': importe,
                'desglosado':importe_neto_desglosado,
            },
            'impuestos':{
                'total': impuestos_desglosado['iva'][condicion_pago_txt],
                'desglosado':impuestos_desglosado,
            },
            'descuento':descuento,
            'campos_particulares':campos_particulares,
        }

        kwargs = {'totales': totales,}

        return kwargs, error, msg

class CuentasXPagarDocumentoImportes(CuentasXPagarDocumentoImportesBase):
   pass

class CuentasXPagarDocumentoImportesImpuesto(CuentasXPagarDocumentoImportesImpuestoBase):
    pass

class CuentasXPagarDocumentoCargoLibres(CuentasXPagarDocumentoCargoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
################################################################
####                                                        ####
####               MODELOS CUENTAS POR COBRAR               ####
####                                                        ####
################################################################

# CATALOGOS

class CuentasXCobrarConcepto(CuentasXCobrarConceptoBase):
    pass

# DOCUMENTOS

class CuentasXCobrarDocumento(CuentasXCobrarDocumentoBase, models.Model):
    def get_totales(self, cuenta_contado = None):
        error = 0
        msg = ''
        
        try:
            cuenta_cliente =  ContabilidadCuentaContable.objects.get(cuenta=self.cliente.cuenta_xcobrar).cuenta
        except ObjectDoesNotExist:
            cuenta_cliente = None

        #Para saber si es contado o es credito
        campos_particulares = []
        if self.naturaleza_concepto == 'C':
            try:
                es_contado = self.condicion_pago == cuenta_contado
            except ObjectDoesNotExist:    
                es_contado = True
                error = 1
                msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% self.folio

            try:
                campos_particulares = CuentasXCobrarDocumentoCargoLibres.objects.get(pk=self.id)
            except ObjectDoesNotExist:
                campos_particulares =[]

        elif self.naturaleza_concepto == 'R':
            es_contado = True
            try:
                campos_particulares = CuentasXCobrarDocumentoCreditoLibres.objects.get(pk=self.id)
            except ObjectDoesNotExist:
                campos_particulares =[]

        if not campos_particulares == []:
            campos_particulares = campos_particulares

        importesDocto       = CuentasXCobrarDocumentoImportes.objects.filter(docto_cc=self, cancelado='N')

        impuestos       = 0
        importe     = 0
        total           = 0
        iva_retenido    = 0
        isr_retenido = 0
        descuento           = 0

        for importeDocumento in importesDocto:
            impuestos       = impuestos + (importeDocumento.total_impuestos * self.tipo_cambio)
            importe         = importe + (importeDocumento.importe * self.tipo_cambio)
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

        kwargs = {
            'ventas'              : ventas,
            'impuestos'           : impuestos,
            'iva_retenido'        : iva_retenido,
            'isr_retenido'        : isr_retenido,
            'descuento'           : descuento,
            'clientes'            : clientes,
            'cuenta_cliente'      : cuenta_cliente,
            'bancos'              : bancos,
            'campos_particulares' : campos_particulares,
        }
        
        return kwargs, error, msg
    
class CuentasXCobrarDocumentoImportes(CuentasXCobrarDocumentoImportesBase):
    pass

class CuentasXCobrarDocumentoImportesImpuesto(CuentasXCobrarDocumentoImportesImpuestoBase): 
    pass

class CuentasXCobrarDocumentoCargoVencimiento(CuentasXCobrarDocumentoCargoVencimientoBase):
    pass

class CuentasXCobrarDocumentoCargoLibres(CuentasXCobrarDocumentoCargoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
class CuentasXCobrarDocumentoCreditoLibres(CuentasXCobrarDocumentoCreditoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
    
################################################################
####                                                        ####
####               MODELOS CONTABILIDAD                     ####
####                                                        ####
################################################################

# CATALOGOS

class ContabilidadCuentaContable(ContabilidadCuentaContableBase):
    pass

# DOCUMENTOS

class ContabilidadGrupoPolizaPeriodo(ContabilidadGrupoPolizaPeriodoBase):
    pass

class ContabilidadRecordatorio(ContabilidadRecordatorioBase):
    pass

class ContabilidadDocumento(ContabilidadDocumentoBase):
    def next_folio( self, using=None):
        """ Generar un folio nuevo de una poliza e incrementa el consecutivo de folios """
        tipo_poliza = self.tipo_poliza
        prefijo = tipo_poliza.prefijo
        if not prefijo:
            prefijo = ''
        tipo_consecutivo = tipo_poliza.tipo_consec

        try:
            if tipo_consecutivo == 'M':
                tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, mes= self.fecha.month, ano = self.fecha.year)
            elif tipo_consecutivo == 'E':
                tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, ano=self.fecha.year, mes=0)
            elif tipo_consecutivo == 'P':
                tipo_poliza_det = TipoPolizaDetalle.objects.get(tipo_poliza = tipo_poliza, mes=0, ano =0)
        except ObjectDoesNotExist:
            if tipo_consecutivo == 'M':      
                tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', using), tipo_poliza=tipo_poliza, ano=self.fecha.year, mes=self.fecha.month, consecutivo = 1,)
            elif tipo_consecutivo == 'E':
                #Si existe permanente toma su consecutivo para crear uno nuevo si no existe inicia en 1
                consecutivo = TipoPolizaDetalle.objects.filter(tipo_poliza = tipo_poliza, mes=0, ano =0).aggregate(max = Sum('consecutivo'))['max']

                if consecutivo == None:
                    consecutivo = 1

                tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', using), tipo_poliza=tipo_poliza, ano= self.fecha.year, mes=0, consecutivo=consecutivo,)
            elif tipo_consecutivo == 'P':
                consecutivo = TipoPolizaDetalle.objects.all().aggregate(max = Sum('consecutivo'))['max']

                if consecutivo == None:
                    consecutivo = 1

                tipo_poliza_det = TipoPolizaDetalle.objects.create(id=next_id('ID_CATALOGOS', using), tipo_poliza=tipo_poliza, ano=0, mes=0, consecutivo = consecutivo,)                                
        
        folio = '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]) 

        #CONSECUTIVO DE FOLIO DE POLIZA
        tipo_poliza_det.consecutivo += 1 
        tipo_poliza_det.save()
        
        return folio
    
    def save(self, *args, **kwargs):
        
        if not self.poliza:
            kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
            self.poliza = self.next_folio(using=kwargs['using'])

        super(self.__class__, self).save(*args, **kwargs)

class ContabilidadDocumentoDetalle(ContabilidadDocumentoDetalleBase):
    pass

# LISTAS

class TipoPoliza(TipoPolizaBase):
    pass

class TipoPolizaDetalle(TipoPolizaDetalleBase):
    pass

class ContabilidadDepartamento(ContabilidadDepartamentoBase):
    pass

################################################################
####                                                        ####
####                    MODELOS VENTAS                      ####
####                                                        ####
################################################################

# DOCUMENTOS
class VentasDocumento(VentasDocumentoBase):

    def get_descuento_total(self, **kwargs):
        
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))

        c = connections[kwargs['using']].cursor()
        c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_VE(%s,'S') AS  A;"% self.id)
        row = c.fetchone()
        return int(row[0])

    def get_totales(self, cuenta_contado= None):  
        
        error = 0
        msg = ''
        
        #CAMPOS PARTICULARES
        if self.tipo == 'F':
            campos_particulares = VentasDocumentoFacturaLibres.objects.filter(pk=self.id)[0]
        #Si es una devolucion
        elif self.tipo == 'D':
            campos_particulares = VentasDocumentoFacturaDevLibres.objects.filter(pk=self.id)[0]
        
        #CUENTA_CONTABLE
        try:
            cuenta_contable =  ContabilidadCuentaContable.objects.get(cuenta=self.cliente.cuenta_xcobrar).cuenta
        except ObjectDoesNotExist:
            cuenta_contable = None
        
        #CONTADO/CREDITO
        try:
            es_contado = self.condicion_pago == cuenta_contado
        except ObjectDoesNotExist:    
            es_contado = True
            error = 1
            msg='El documento con folio[%s] no tiene condicion de pago indicado, por favor indicalo para poder generar las polizas.'% self.folio

        if es_contado:
            condicion_pago_txt = 'contado'
        elif not es_contado:
            condicion_pago_txt = 'credito'
        
        #DESCUENTO
        descuento = self.get_descuento_total()

        importe_neto_desglosado = {
            'iva_0':{'contado':0,'credito':0,},
            'iva'  :{'contado':0,'credito':0,},
            'ieps'  :{'contado':0,'credito':0,},
        }

        impuestos_desglosado = {
            'iva': {'contado':0,'credito':0,},
            'ieps':{'contado':0,'credito':0,}
        }

        documento_impuestos = VentasDocumentoImpuesto.objects.filter(documento=self).values_list('impuesto','importe','venta_neta','porcentaje')

        for documento_impuesto_list in documento_impuestos:
            documento_impuesto = {
                'tipo': Impuesto.objects.get(pk=documento_impuesto_list[0]).tipoImpuesto,
                'importe':documento_impuesto_list[1],
                'venta_neta':documento_impuesto_list[2],
                'porcentaje': documento_impuesto_list[3],
            }

            #Si es impuesto tipo IVA (16,15,etc.)
            if documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'V' and documento_impuesto['porcentaje'] > 0:
                importe_neto_desglosado['iva'][condicion_pago_txt] = documento_impuesto['venta_neta']
                impuestos_desglosado['iva'][condicion_pago_txt]  = documento_impuesto['importe']
            #Si es IVA al 0
            elif documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'V' and documento_impuesto['porcentaje'] == 0:
                importe_neto_desglosado['iva_0'][condicion_pago_txt] = documento_impuesto['venta_neta']
            #Si es IEPS
            elif documento_impuesto['tipo'].tipo == 'I' and documento_impuesto['tipo'].id_interno == 'P':
                importe_neto_desglosado['ieps'][condicion_pago_txt] += documento_impuesto['venta_neta']
                # venta_neta_ieps[condicion_pago_txt] = venta_neta_ieps[condicion_pago_txt] + documento_impuesto['venta_neta']
                impuestos_desglosado['ieps'][condicion_pago_txt] += documento_impuesto['importe']
    
        #si llega a  haber un proveedor que no tenga cargar impuestos
        if importe_neto_desglosado['iva']['contado'] < 0 or importe_neto_desglosado['iva']['credito'] < 0:
            msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
            if crear_polizas_por == 'Dia':
                msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

            error = 1
        
        totales = {
            'a_nombre_de': {
                'tipo':'cliente',
                'id':self.cliente.id,
                'cuenta_contable':cuenta_contable,
            },
            'movimiento':'salida',
            'folio':self.folio,
            'condicion_pago': condicion_pago_txt,
            'retenciones_total': 0,
            'importe_neto':{
                'total': self.importe_neto,
                'desglosado':importe_neto_desglosado,
            },
            'impuestos':{
                'total': self.impuestos_total,
                'desglosado':impuestos_desglosado,
            },
            'campos_particulares':campos_particulares,
            'descuento':0,
        }
        
        kwargs = {'totales':totales,}
        return kwargs, error, msg

    def next_folio( self, connection_name=None, **kwargs ):
        ''' Funcion para generar el siguiente folio de un documento de ventas '''

        #Parametros opcionales
        serie = kwargs.get('serie', None)
        consecutivos_folios = FolioVenta.objects.using(connection_name).filter(tipo_doc = self.tipo, modalidad_facturacion = self.modalidad_facturacion)
        if serie:
            consecutivos_folios = consecutivos_folios.filter(serie=serie)

        consecutivo_row = first_or_none(consecutivos_folios)
        consecutivo = ''
        if consecutivo_row:
            consecutivo = consecutivo_row.consecutivo 
            serie = consecutivo_row.serie
            if serie == u'@':
                serie = ''

        folio = '%s%s'% (serie,("%09d" % int(consecutivo))[len(serie):]) 

        consecutivo_row.consecutivo = consecutivo_row.consecutivo + 1
        consecutivo_row.save(using=connection_name)

        return folio, consecutivo

    def save(self, *args, **kwargs):
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))

        consecutivo = ''
        #Si no se define folio se asigna uno
        if self.folio == '':
            self.folio, consecutivo = self.next_folio(connection_name=kwargs['using'])
        super(self.__class__, self).save(*args, **kwargs)

        #si es factura 
        if consecutivo != '' and self.tipo == 'F' and self.modalidad_facturacion == 'CFDI':
            folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.using(kwargs['using']).filter(modalidad_facturacion=self.modalidad_facturacion))
            if not folios_fiscales:
                ConfiguracionFolioFiscal.objects.using(kwargs['using']).create(
                        serie = '@',
                        folio_ini = 1,
                        folio_fin = 999999999,
                        ultimo_utilizado = 0,
                        num_aprobacion ="1",
                        ano_aprobacion = 1,
                        modalidad_facturacion = self.modalidad_facturacion,
                    )
                folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.using(kwargs['using']).filter(modalidad_facturacion=self.modalidad_facturacion))

            if folios_fiscales:
                ConfiguracionFolioFiscalUso.objects.using(kwargs['using']).create(
                        id= -1,
                        folios_fiscales = folios_fiscales,
                        folio= consecutivo,
                        fecha = datetime.now(),
                        sistema = self.sistema_origen,
                        documento = self.id,
                        xml = '',
                    )


class VentasDocumentoVencimiento(VentasDocumentoVencimientoBase):
    pass

class VentasDocumentoImpuesto(VentasDocumentoImpuestoBase):
    pass

class VentasDocumentoDetalle(VentasDocumentoDetalleBase):
    pass

class VentasDocumentoLiga(VentasDocumentoLigaBase):
    pass

class VentasDocumentoFacturaLibres(VentasDocumentoFacturaLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')

class VentasDocumentoFacturaDevLibres(VentasDocumentoFacturaDevLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')

################################################################
####                                                        ####
####                MODELOS PUNTO DE VENTAS                 ####
####                                                        ####
################################################################

#LISTAS

class Cajero(CajeroBase):
    pass

class Caja(CajaBase):
    pass

class CajaFolios(CajaFoliosBase):
    pass 

class CajeroCaja(CajeroCajaBase):
    pass
class FormaCobro(FormaCobroBase):
    pass

class FormaCobroReferencia(FormaCobroReferenciaBase):
    pass

#DOCUMENTOS

class PuntoVentaDocumento(PuntoVentaDocumentoBase):

    def next_folio( self, connection_name=None, **kwargs ):
        ''' Funcion para generar el siguiente folio de un documento de ventas '''
        
        #Parametros opcionales
        serie = kwargs.get('serie', None)
        
        if self.tipo == 'F':
            consecutivos_folios = FolioVenta.objects.using(connection_name).filter(tipo_doc = self.tipo, modalidad_facturacion = self.modalidad_facturacion)
            if serie:
                consecutivos_folios = consecutivos_folios.filter(serie=serie)

            consecutivo_row = first_or_none(consecutivos_folios)
            consecutivo = ''
            if consecutivo_row:
                consecutivo = consecutivo_row.consecutivo 
                serie = consecutivo_row.serie
                if serie == u'@':
                    serie = ''

            consecutivo_row.consecutivo = consecutivo_row.consecutivo + 1
            consecutivo_row.save()

        elif self.tipo == 'V':
            caja_folios_list =  CajaFolios.objects.filter(caja= self.caja, documento_tipo = self.tipo).values_list( 'serie', 'consecutivo')[0]
            serie = caja_folios_list[0]
            consecutivo = caja_folios_list[1]

            c = connections[connection_name].cursor()
            query = '''UPDATE FOLIOS_CAJAS set CONSECUTIVO=%s WHERE CAJA_ID = %s and TIPO_DOCTO = %s;'''
            c.execute(query,[consecutivo+1, self.caja.id, self.tipo])
            c.close()
            # management.call_command( 'syncdb', database = using, interactive= False)

        folio = '%s%s'% (serie,("%09d" % int(consecutivo))[len(serie):]) 

        return folio, consecutivo - 1

    def save(self, *args, **kwargs):
        kwargs['using'] = kwargs.get('using', router.db_for_write(self.__class__, instance=self))
        
        consecutivo = ''
        #Si no se define folio se asigna uno
        if self.folio == '':
            self.folio, consecutivo = self.next_folio(connection_name=kwargs['using'])

        super(self.__class__, self).save(*args, **kwargs)
        
        #si es factura 
        if consecutivo != '' and self.tipo == 'F' and self.modalidad_facturacion == 'CFDI':
            folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.using(kwargs['using']).filter(modalidad_facturacion=self.modalidad_facturacion))
            if folios_fiscales:
                ConfiguracionFolioFiscalUso.objects.using(kwargs['using']).create(
                        id= -1,
                        folios_fiscales = folios_fiscales,
                        folio= consecutivo,
                        fecha = datetime.now(),
                        sistema = self.sistema_origen,
                        documento = self.id,
                        xml = '',
                    )


class PuntoVentaDocumentoDetalle(PuntoVentaDocumentoDetalleBase):
    pass
    
class PuntoVentaDocumentoLiga(PuntoVentaDocumentoLigaBase):
    pass

class PuntoVentaDocumentoLigaDetalle(PuntoVentaDocumentoLigaDetalleBase):
    pass

class PuntoVentaDocumentoDetalleTransferencia(PuntoVentaDocumentoDetalleTransferenciaBase):
    pass

class PuntoVentaCobro(PuntoVentaCobroBase):
    pass

class PuntoVentaCobroReferencia(PuntoVentaCobroReferenciaBase):
    pass

class PuntoVentaDocumentoImpuesto(PuntoVentaDocumentoImpuestoBase):
    pass

class PuntoVentaDocumentoImpuestoGravado(PuntoVentaDocumentoImpuestoGravadoBase):
    pass