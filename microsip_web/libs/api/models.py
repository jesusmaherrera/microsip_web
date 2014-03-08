#encoding:utf-8
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db import router
from django.core.cache import cache
from django.db import connections, transaction, DatabaseError
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.core import management
from django.contrib.sessions.models import Session
from microsip_web.apps.config.models import Usuario
from microsip_web.libs.custom_db.main import next_id, first_or_none, firstid_or_none, firstALMACENid_or_none
import django.dispatch

articulo_clave_save_signal = django.dispatch.Signal()
plazo_condicion_pago_save_signal = django.dispatch.Signal()

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

class Pais(PaisBase):
    pass
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
        
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  

        if self.es_predet == 'S':
            Pais.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.nombre

class Estado(EstadoBase):
    
    def save(self, *args, **kwargs):
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
            
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
        
        if self.es_predet == 'S':
            Estado.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s' % (self.nombre, self.pais)

class Ciudad(CiudadBase):
    def save(self, *args, **kwargs):
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
            
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  

        if self.es_predet == 'S':
            Ciudad.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s'%(self.nombre, self.estado)

class Moneda(MonedaBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class PrecioEmpresa(PrecioEmpresaBase):
    def __unicode__(self):
        return u'%s' % self.nombre

#articulos
class Carpeta(models.Model):
    nombre  = models.CharField(max_length=30)
    carpeta_padre = models.ForeignKey('self', related_name='carpeta_padre_a', blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.nombre
    class Meta:
        db_table = u'sic_carpeta'

class GrupoLineas(GrupoLineasBase):
    puntos = models.IntegerField(blank=True, null=True, db_column='SIC_PUNTOS')
    dinero_electronico = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.nombre

class LineaArticulos(LineaArticulosBase):
    
    puntos = models.IntegerField(blank=True, null=True, db_column='SIC_PUNTOS')
    dinero_electronico = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')
    hereda_puntos = models.BooleanField( db_column='SIC_HEREDA_PUNTOS')

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
        super(self.__class__, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return u'%s' % self.nombre

class Articulo(ArticuloBase):
    
    puntos = models.IntegerField(default = 0, blank = True, null = True, db_column = 'SIC_PUNTOS' )
    dinero_electronico  = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_DINERO_ELECTRONICO' )
    hereda_puntos = models.BooleanField( db_column = 'SIC_HEREDA_PUNTOS' )
    carpeta = models.ForeignKey( Carpeta, blank = True, null = True, db_column = 'SIC_CARPETA_ID' )

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(self.__class__, self).save(*args, **kwargs)
        
    def __unicode__( self) :
        return u'%s (%s)' % ( self.nombre, self.unidad_venta )

class PrecioArticulo(ArticuloPrecioBase):
    def __unicode__(self):
        return u'%s' % self.id
#clientes

class ClienteTipo(ClienteTipoBase):
    
    valor_puntos    = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_VALOR_PUNTOS' )

    def __unicode__( self ):
        return self.nombre

class CondicionPago(CondicionPagoBase):
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if not self.id:
            self.id = next_id('ID_CATALOGOS', using)
        
        if self.es_predet == 'S':
            CondicionPago.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre

class CondicionPagoPlazo(CondicionPagoPlazoBase):
    def save_send_signal(self, *args, **kwargs):
        articulo_clave_save_signal.send(sender=self, *args, **kwargs)
        
    def save(self, *args, **kwargs):    
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class Cliente(ClienteBase):

    TIPOS = ( ( 'N', 'No Aplica' ),( 'P', 'Puntos' ),( 'D', 'Dinero Electronico' ), )
    puntos = models.IntegerField(default = 0, blank = True, null = True, db_column = 'SIC_PUNTOS' )
    dinero_electronico = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_DINERO_ELECTRONICO' )
    tipo_tarjeta = models.CharField( default = 'N', max_length = 1, choices = TIPOS, db_column = 'SIC_TIPO_TARJETA' )
    hereda_valorpuntos = models.BooleanField( db_column = 'SIC_HEREDA_VALORPUNTOS' )
    valor_puntos = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_VALOR_PUNTOS' )
    hereda_puntos_a = models.ForeignKey( 'self', db_column = 'SIC_HEREDAR_PUNTOS_A', related_name = 'hereda_puntos_a_cliente', blank = True, null = True )

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__( self ):
        return self.nombre

class ClienteClaveRol(ClienteClaveRolBase):
    pass

class ClavesClientes(ClienteClaveBase):
    def __unicode__(self):
        return self.clave

class ClienteDireccion(ClienteDireccionBase):
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
            
        super(self.__class__, self).save(*args, **kwargs)
    
class libresClientes(libreClienteBase):
    heredar_puntos_a = models.CharField(max_length=99, db_column='HEREDAR_PUNTOS_A')
    cuenta_1 = models.CharField(max_length=99, db_column='CUENTA_1')
    cuenta_2 = models.CharField(max_length=99, db_column='CUENTA_2')
    cuenta_3 = models.CharField(max_length=99, db_column='CUENTA_3')
    cuenta_4 = models.CharField(max_length=99, db_column='CUENTA_4')
    cuenta_5 = models.CharField(max_length=99, db_column='CUENTA_5')

#listas
class ImpuestoTipo(ImpuestoTipoBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class Impuesto(ImpuestoBase):
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
        
        if self.es_predet == 'S':
            Impuesto.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.nombre
    
class ImpuestosArticulo(ImpuestoArticuloBase):
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(self.__class__, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.impuesto

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
        
########################################################################################################
        
class TipoCambio(TipoCambioBase):
    def __unicode__(self):
        return u'%s' % self.id

class Registry(RegistryBase):
    def __unicode__(self):
        return u'%s' % self.nombre
    
    def get_value(self):
        if self.valor == '':
            return None
        return self.valor

class CondicionPagoCp(CuentasXPagarCondicionPagoBase):
    def __unicode__(self):
        return self.nombre

class CondicionPagoCPPlazo(CuentasXPagarCondicionPagoPlazoBase):
    def save(self, *args, **kwargs):    
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class TipoProveedor(TipoProveedorBase):
    def __unicode__(self):
        return u'%s' % self.nombre
        
class Proveedor(ProveedorBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class FolioFiscal(ConfiguracionFolioFiscalBase): 
    def __str__(self):  
          return u'%s' % self.id

class UsoFoliosFiscales(ConfiguracionFolioFiscalUsoBase):
    def __str__(self):  
          return u'%s' % self.id    
          
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class FolioCompra(FolioCompraBase):
    def __unicode__(self):
        return u'%s'%self.id

class Aduana(AduanaBase):
    class Meta:
        db_table = u'aduanas'

class Almacen(AlmacenBase):
    inventariando = models.BooleanField(default= False, db_column = 'SIC_INVENTARIANDO' )
    inventario_conajustes = models.BooleanField(default= False, db_column = 'SIC_INVCONAJUSTES' )
    inventario_modifcostos = models.BooleanField(default= False, db_column = 'SIC_INVMODIFCOSTOS' )

    def __unicode__(self):
        return self.nombre

class ArticuloDiscreto(ArticuloDiscretoBase):
    def __unicode__(self):
        return u'%s' % self.clave

class ExistDiscreto(ArticuloDiscretoExistenciaBase):
    def __unicode__(self):
        return u'%s' % self.id

class Bancos(BancoBase):
    pass

class Pedimento(PedimentoBase):
    pass

class CentrosCosto(InventariosCentroCostosBase):
    def __unicode__(self):
        return self.nombre 
    
class ArticuloClaveRol(ArticuloClaveRolBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class ClavesArticulos(ArticuloClaveBase):
    def save_send_signal(self, *args, **kwargs):
        articulo_clave_save_signal.send(sender=self, *args, **kwargs)

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.clave

class ConceptosIn(InventariosConcepto):
    def __unicode__(self):
        return self.nombre_abrev

class ConsignatarioCompras(ComprasConsignatarioBase):
    pass

class CuentaCo(ContabilidadCuentaContableBase):
    def __unicode__(self):
        return u'%s (%s)' % (self.cuenta, self.nombre)
    
class DocumentoCompras(ComprasDocumentoBase):
    
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
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

            consecutivo = ''
            #Si no se define folio se asigna uno
            if self.folio == '':
                self.folio = self.next_folio(connection_name=using)

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.id

class VencimientoCargoCompra(ComprasDocumentoCargoVencimientoBase):
    pass

class DocumentoComprasDetalle(ComprasDocumentoDetalleBase):
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class DocumentoComprasImpuesto(ComprasDocumentoImpuestoBase):
   pass

class DocumentoComprasLiga(ComprasDocumentoLigaBase):
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class DocumentoComprasDetalleLiga(ComprasDocumentoLigaDetalleBase):
    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )

##########################################
##                                      ##
##             INVENTARIOS              ##
##                                      ##
##########################################

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
        
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

            #Si no se define folio se asigna uno
            if not self.folio and self.concepto.folio_autom == 'S':
                self.folio = self.next_folio()

        super(self.__class__, self).save(*args, **kwargs)

class InventariosDocumentoDetalle(InventariosDocumentoDetalleBase):
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='SIC_FECHAHORA_U')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='SIC_USUARIO_ULT_MODIF')
    detalle_modificacionestime = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLETIME_MODIFICACIONES')
    
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.id

class InventariosDesgloseEnDiscretos(InventariosDesgloseEnDiscretosBase):
    def __unicode__(self):
        return u'%s' % self.id

class InventariosDocumentoIF(InventariosDocumentoIFBase):
    def __unicode__(self):
        return u'%s' % self.id
    
class InventariosDocumentoIFDetalle(InventariosDocumentoIFDetalleBase):
    def __unicode__(self):
        return u'%s' % self.id

class InventariosDesgloseEnDiscretosIF(InventariosDesgloseEnDiscretosIFBase):
    def __unicode__(self):
        return u'%s' % self.id

################################################################
####                                                        ####
####               MODELOS CUENTAS POR PAGAR                ####
####                                                        ####
################################################################


class CuentasXPagarConcepto(CuentasXPagarConceptoBase):
    def __unicode__(self):
        return self.nombre_abrev

class CuentasXPagarDocumento(CuentasXPagarDocumentoBase):
    def __unicode__(self):
        return u'%s' % self.id

class CuentasXPagarDocumentoImportes(CuentasXPagarDocumentoImportesBase):
   pass

class CuentasXPagarDocumentoCargoLibres(CuentasXPagarDocumentoCargoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
    def __unicode__(self):
        return u'%s' % self.id


################################################################
####                                                        ####
####               MODELOS CUENTAS POR COBRAR               ####
####                                                        ####
################################################################

class CuentasXCobrarConcepto(CuentasXCobrarConceptoBase):
    def __unicode__(self):
        return self.nombre_abrev

class CuentasXCobrarDocumento(CuentasXCobrarDocumentoBase):
    def __unicode__(self):
        return u'%s' % self.id

class CuentasXCobrarDocumentoImportes(CuentasXCobrarDocumentoImportesBase):
    def __unicode__(self):
        return u'%s' % self.id

class CuentasXCobrarDocumentoCargoLibres(CuentasXCobrarDocumentoCargoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    def __unicode__(self):
        return u'%s' % self.id

class CuentasXCobrarDocumentoCreditoLibres(CuentasXCobrarDocumentoCreditoLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
    def __unicode__(self):
        return u'%s' % self.id
    
################################################################
####                                                        ####
####               MODELOS CONTABILIDAD                     ####
####                                                        ####
################################################################

class ContabilidadDepartamento(ContabilidadDepartamentoBase):
    def __unicode__(self):
        return u'%s' % self.clave

class ContabilidadRecordatorio(ContabilidadRecordatorioBase):
    pass

class ContabilidadGrupoPolizaPeriodo(ContabilidadGrupoPolizaPeriodoBase):
    pass

class TipoPoliza(TipoPolizaBase):
    def __unicode__(self):
        return u'%s' % self.nombre 

class TipoPolizaDetalle(TipoPolizaDetalleBase):
    def __unicode__(self):
        return u'%s' % self.id

class ContabilidadDocumento(ContabilidadDocumentoBase):
    def __unicode__(self):
        return u'%s' % self.id

class ContabilidadDocumentoDetalle(ContabilidadDocumentoDetalleBase):
    pass

################################################################
####                                                        ####
####                    MODELOS VENTAS                      ####
####                                                        ####
################################################################

class Vendedor(VendedorBase):
    def __unicode__(self):
        return self.nombre

class ViaEmbarque(ViaEmbarqueBase):
   pass

class FolioVenta(FolioVentaBase):
    def __unicode__(self):
        return u'%s'%self.id

class VentasDocumento(VentasDocumentoBase):
    def __unicode__(self):
        return u'%s' % self.id

class VentasDocumentoVencimiento(VentasDocumentoVencimientoBase):
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

    def __unicode__(self):
        return u'%s' % self.id
    
class VentasDocumentoFacturaDevLibres(VentasDocumentoFacturaDevLibresBase):
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')

    def __unicode__(self):
        return u'%s' % self.id

################################################################
####                                                        ####
####                MODELOS PUNTO DE VENTAS                 ####
####                                                        ####
################################################################

#LISTAS
class Cajero(CajeroBase):
    def __unicode__(self):
        return self.nombre

class Caja(CajaBase):
    def __unicode__(self):
        return self.nombre 

class Forma_cobro(FormaCobroBase):
    def __unicode__(self):
        return self.nombre

class Forma_cobro_refer(FormaCobroReferenciaBase):
    def __unicode__(self):
        return self.nombre

#DOCUMENTOS
class Docto_PV(PuntoVentaDocumentoBase): 
    puntos                  = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico      = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')

    def __unicode__( self ):
        return u'%s'% self.folio
    
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
        consecutivo_row.save()

        return folio, consecutivo - 1


    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)
            consecutivo = ''
            #Si no se define folio se asigna uno
            if self.folio == '':
                self.folio, consecutivo = self.next_folio(connection_name=using)

            #si es factura 
            if consecutivo != '' and self.tipo == 'F' and self.modalidad_facturacion == 'CFDI':
                folios_fiscales = first_or_none(FolioFiscal.objects.filter(modalidad_facturacion=self.modalidad_facturacion))
                if folios_fiscales:
                    UsoFoliosFiscales.objects.create(
                            id= -1,
                            folios_fiscales = folios_fiscales,
                            folio= consecutivo,
                            fecha = datetime.now(),
                            sistema = self.sistema_origen,
                            documento = self.id,
                            xml = '',
                        )

        super(self.__class__, self).save(*args, **kwargs)

class Docto_pv_det(PuntoVentaDocumentoDetalleBase):
    def __unicode__(self):
        return u'%s(%s)'% (self.id, self.documento_pv)
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class DoctoPVLiga(PuntoVentaDocumentoLigaBase):
    def __unicode__(self):
        return u'%s'% self.id 
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class DoctoPVLigaDet(PuntoVentaDocumentoLigaDetalleBase):
    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )

class Docto_pv_det_tran_elect(PuntoVentaDocumentoDetalleTransferenciaBase):
    def __unicode__(self):
        return u'%s'% self.id 

class Docto_pv_cobro(PuntoVentaCobroBase):
    def __unicode__(self):
        return u'%s'% self.id

class Docto_pv_cobro_refer(PuntoVentaCobroReferenciaBase):
    def __unicode__(self):
        return u'%s'% self.id 

class Impuestos_docto_pv(PuntoVentaDocumentoImpuestoBase):
    pass

class Impuestos_grav_docto_pv(PuntoVentaDocumentoImpuestoGravadoBase):
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