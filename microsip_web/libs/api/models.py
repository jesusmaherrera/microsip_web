#encoding:utf-8
from django.db import models
from django.db import router
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sessions.models import Session

from microsip_api.comun.sic_db import next_id, first_or_none
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

################################################################
####                                                        ####
####                      MODELOS OTROS                     ####
####                                                        ####
################################################################

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
    def __unicode__(self):
        return u'%s' % self.nombre
    
    def get_value(self):
        if self.valor == '':
            return None
        return u"%s"%self.valor

#FOLIOS FISCALES

class ConfiguracionFolioFiscal(ConfiguracionFolioFiscalBase): 
    def __str__(self):  
          return u'%s' % self.id
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class ConfiguracionFolioFiscalUso(ConfiguracionFolioFiscalUsoBase):
    def __str__(self):  
          return u'%s' % self.id    
          
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)


################################################################
####                                                        ####
####                        COMUN                           ####
####                                                        ####
################################################################

# OTROS
    
class Pais(PaisBase):
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

class TipoCambio(TipoCambioBase):
    def __unicode__(self):
        return u'%s' % self.id

class ViaEmbarque(ViaEmbarqueBase):
   pass

class FolioVenta(FolioVentaBase):
    def __unicode__(self):
        return u'%s'%self.id

class FolioCompra(FolioCompraBase):
    def __unicode__(self):
        return u'%s'%self.id

# ARTICULOS

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

class ArticuloClaveRol(ArticuloClaveRolBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class ArticuloClave(ArticuloClaveBase):
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

class ArticuloPrecio(ArticuloPrecioBase):
    def __unicode__(self):
        return u'%s' % self.id

class Almacen(AlmacenBase):
    inventariando = models.BooleanField(default= False, db_column = 'SIC_INVENTARIANDO' )
    inventario_conajustes = models.BooleanField(default= False, db_column = 'SIC_INVCONAJUSTES' )
    inventario_modifcostos = models.BooleanField(default= False, db_column = 'SIC_INVMODIFCOSTOS' )
    
    def __unicode__(self):
        return self.nombre

class PrecioEmpresa(PrecioEmpresaBase):
    def __unicode__(self):
        return u'%s' % self.nombre

class ArticuloDiscreto(ArticuloDiscretoBase):
    def __unicode__(self):
        return u'%s' % self.clave

class ArticuloDiscretoExistencia(ArticuloDiscretoExistenciaBase):
    def __unicode__(self):
        return u'%s' % self.id

#CATALOGOS

class Banco(BancoBase):
    pass

# LISTAS

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

class Vendedor(VendedorBase):
    def __unicode__(self):
        return self.nombre


# CLIENTES

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

class ClienteClave(ClienteClaveBase):
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

# PROVEEDORES

class ProveedorTipo(ProveedorTipoBase):
    def __unicode__(self):
        return u'%s' % self.nombre
        
class Proveedor(ProveedorBase):
    def __unicode__(self):
        return u'%s' % self.nombre


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

class ComprasDocumentoCargoVencimiento(ComprasDocumentoCargoVencimientoBase):
    pass

class ComprasDocumentoDetalle(ComprasDocumentoDetalleBase):
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class ComprasDocumentoImpuesto(ComprasDocumentoImpuestoBase):
   pass

class ComprasDocumentoLiga(ComprasDocumentoLigaBase):
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class ComprasDocumentoLigaDetalle(ComprasDocumentoLigaDetalleBase):
    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )


#####################################################
##
##                         INVENTARIOS
##
##
#####################################################

# CATALOGOS

class InventariosConcepto(InventariosConceptoBase):
    def __unicode__(self):
        return self.nombre_abrev

class InventariosCentroCostos(InventariosCentroCostosBase):
    def __unicode__(self):
        return self.nombre 

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

class InventariosDocumentoIF(InventariosDocumentoIFBase):
    def __unicode__(self):
        return u'%s' % self.id

class InventariosDocumentoIFDetalle(InventariosDocumentoIFDetalleBase):
    def __unicode__(self):
        return u'%s' % self.id

# OTROS

class InventariosDesgloseEnDiscretos(InventariosDesgloseEnDiscretosBase):
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

# CATALOGOS

class CuentasXPagarConcepto(CuentasXPagarConceptoBase):
    def __unicode__(self):
        return self.nombre_abrev

class CuentasXPagarCondicionPago(CuentasXPagarCondicionPagoBase):
    def __unicode__(self):
        return self.nombre

class CuentasXPagarCondicionPagoPlazoBase(CuentasXPagarCondicionPagoPlazoBase):
    def save(self, *args, **kwargs):    
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)

        super(self.__class__, self).save(*args, **kwargs)

# DOCUMENTOS

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

# CATALOGOS

class CuentasXCobrarConcepto(CuentasXCobrarConceptoBase):
    def __unicode__(self):
        return self.nombre_abrev

# DOCUMENTOS

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

# CATALOGOS

class ContabilidadCuentaContable(ContabilidadCuentaContableBase):
    def __unicode__(self):
        return u'%s (%s)' % (self.cuenta, self.nombre)

# DOCUMENTOS

class ContabilidadGrupoPolizaPeriodo(ContabilidadGrupoPolizaPeriodoBase):
    pass

class ContabilidadRecordatorio(ContabilidadRecordatorioBase):
    pass

class ContabilidadDocumento(ContabilidadDocumentoBase):
    def __unicode__(self):
        return u'%s' % self.id

class ContabilidadDocumentoDetalle(ContabilidadDocumentoDetalleBase):
    pass

# LISTAS

class TipoPoliza(TipoPolizaBase):
    def __unicode__(self):
        return u'%s' % self.nombre 

class TipoPolizaDetalle(TipoPolizaDetalleBase):
    def __unicode__(self):
        return u'%s' % self.id

class ContabilidadDepartamento(ContabilidadDepartamentoBase):
    def __unicode__(self):
        return u'%s' % self.clave


################################################################
####                                                        ####
####                    MODELOS VENTAS                      ####
####                                                        ####
################################################################

# DOCUMENTOS

class VentasDocumento(VentasDocumentoBase):

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
        consecutivo_row.save(using=connection_name)

        return folio, consecutivo


    def save(self, *args, **kwargs):
        
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)
            consecutivo = ''
            #Si no se define folio se asigna uno
            if self.folio == '':
                self.folio, consecutivo = self.next_folio(connection_name=using)

            #si es factura 
            if consecutivo != '' and self.tipo == 'F' and self.modalidad_facturacion == 'CFDI':
                folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.using(using).filter(modalidad_facturacion=self.modalidad_facturacion))
                if not folios_fiscales:
                    ConfiguracionFolioFiscal.objects.using(using).create(
                            serie = '@',
                            folio_ini = 1,
                            folio_fin = 999999999,
                            ultimo_utilizado = 0,
                            num_aprobacion ="1",
                            ano_aprobacion = 1,
                            modalidad_facturacion = self.modalidad_facturacion,
                        )
                    folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.using(using).filter(modalidad_facturacion=self.modalidad_facturacion))

                if folios_fiscales:
                    ConfiguracionFolioFiscalUso.objects.using(using).create(
                            id= -1,
                            folios_fiscales = folios_fiscales,
                            folio= consecutivo,
                            fecha = datetime.now(),
                            sistema = self.sistema_origen,
                            documento = self.id,
                            xml = '',
                        )

        super(self.__class__, self).save(*args, **kwargs)

class VentasDocumentoVencimiento(VentasDocumentoVencimientoBase):
    pass

class VentasDocumentoImpuesto(VentasDocumentoImpuestoBase):
    pass

class VentasDocumentoDetalle(VentasDocumentoDetalleBase):
    def __unicode__(self):
        return u'%s(%s)'% (self.id, self.documento_pv)
    
    def save(self, *args, **kwargs):
        
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

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

class FormaCobro(FormaCobroBase):
    def __unicode__(self):
        return self.nombre

class FormaCobroReferencia(FormaCobroReferenciaBase):
    def __unicode__(self):
        return self.nombre

#DOCUMENTOS

class PuntoVentaDocumento(PuntoVentaDocumentoBase): 
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
                folios_fiscales = first_or_none(ConfiguracionFolioFiscal.objects.filter(modalidad_facturacion=self.modalidad_facturacion))
                if folios_fiscales:
                    ConfiguracionFolioFiscalUso.objects.create(
                            id= -1,
                            folios_fiscales = folios_fiscales,
                            folio= consecutivo,
                            fecha = datetime.now(),
                            sistema = self.sistema_origen,
                            documento = self.id,
                            xml = '',
                        )

        super(self.__class__, self).save(*args, **kwargs)

class PuntoVentaDocumentoDetalle(PuntoVentaDocumentoDetalleBase):
    def __unicode__(self):
        return u'%s(%s)'% (self.id, self.documento_pv)
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class PuntoVentaDocumentoLiga(PuntoVentaDocumentoLigaBase):
    def __unicode__(self):
        return u'%s'% self.id 
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(self.__class__, self).save(*args, **kwargs)

class PuntoVentaDocumentoLigaDetalle(PuntoVentaDocumentoLigaDetalleBase):
    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )

class PuntoVentaDocumentoDetalleTransferencia(PuntoVentaDocumentoDetalleTransferenciaBase):
    def __unicode__(self):
        return u'%s'% self.id 

class PuntoVentaCobro(PuntoVentaCobroBase):
    def __unicode__(self):
        return u'%s'% self.id

class PuntoVentaCobroReferencia(PuntoVentaCobroReferenciaBase):
    def __unicode__(self):
        return u'%s'% self.id 

class PuntoVentaDocumentoImpuesto(PuntoVentaDocumentoImpuestoBase):
    pass

class PuntoVentaDocumentoImpuestoGravado(PuntoVentaDocumentoImpuestoGravadoBase):
    pass