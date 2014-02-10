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

@receiver(post_save)
def clear_cache(sender, **kwargs):
    if sender != Session:
        cache.clear()

class SeguimientoFields()
    usuario_creador = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')


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
        

# Trigger.objects.create(nombre='test', descripcion='algo')
# class UserProfile(models.Model):  
#     usuario = models.OneToOneField(User)
#     basedatos_activa = models.CharField(max_length=100)
#     conexion_activa = models.ForeignKey(ConexionDB, blank=True, null=True)

#     def __str__(self):  
#           return "%s's profile" % self.usuario  
    
#     class Meta:
#         app_label =u'auth'

class Carpeta(models.Model):
    nombre  = models.CharField(max_length=30)
    carpeta_padre = models.ForeignKey('self', related_name='carpeta_padre_a', blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.nombre
    class Meta:
        db_table = u'sic_carpeta'
########################################################################################################

class Pais(models.Model):
    id = models.AutoField(primary_key=True, db_column='PAIS_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    nombre_abreviado = models.CharField(max_length=10, db_column='NOMBRE_ABREV')
    
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    def save(self, *args, **kwargs):    
        if self.id == None:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)  

        if self.es_predet == 'S':
            Pais.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(Pais, self).save(*args, **kwargs)  

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'paises'

class Estado(models.Model):
    id = models.AutoField(primary_key=True, db_column='ESTADO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    pais = models.ForeignKey(Pais, db_column='PAIS_ID')
    nombre_abreviado = models.CharField(max_length=10, db_column='NOMBRE_ABREV')
    
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    def save(self, *args, **kwargs):
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
            
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
        
        if self.es_predet == 'S':
            Estado.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(Estado, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s' % (self.nombre, self.pais)

    class Meta:
        db_table = u'estados'

class Ciudad(models.Model):
    id          = models.AutoField(primary_key=True, db_column='CIUDAD_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    estado      = models.ForeignKey(Estado, db_column='ESTADO_ID')
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')
    
    def save(self, *args, **kwargs):
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)
            
        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
        
        if self.es_predet == 'S':
            Ciudad.objects.using(using).all().exclude(pk=self.id).update(es_predet='N')

        super(Ciudad, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s'%(self.nombre, self.estado)

    class Meta:
        db_table = u'ciudades'

class Moneda(models.Model):
    id = models.AutoField(primary_key=True, db_column='MONEDA_ID')
    es_moneda_local = models.CharField(default='N', max_length=1, db_column='ES_MONEDA_LOCAL')
    nombre = models.CharField(max_length=30, db_column='NOMBRE')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'monedas'

class TipoCambio(models.Model, SeguimientoFields):
    id = models.AutoField(primary_key=True, db_column='HISTORIA_CAMB_ID')
    moneda = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    fecha = models.DateField(db_column='FECHA')
    tipo_cambio = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    tipo_cambio_cobros = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO_COBROS')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'historia_cambiaria'
        
class TiposImpuestos(models.Model):
    id      = models.AutoField(primary_key=True, db_column='TIPO_IMPTO_ID')
    nombre  = models.CharField(max_length=30, db_column='NOMBRE')
    tipo    = models.CharField(max_length=30, db_column='TIPO')
    
    def __unicode__(self):
        return u'%s' % self.nombre
    class Meta:
        db_table = u'tipos_impuestos'

class Impuesto(models.Model):
    id = models.AutoField(primary_key=True, db_column='IMPUESTO_ID')
    tipoImpuesto = models.ForeignKey(TiposImpuestos, on_delete= models.SET_NULL, blank=True, null=True, db_column='TIPO_IMPTO_ID')
    nombre = models.CharField(max_length=30, db_column='NOMBRE')
    porcentaje = models.DecimalField(default=0, blank=True, null=True, max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    def save(self, *args, **kwargs):    
        if self.id == None:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)  
        
        if self.es_predet == 'S':
            Impuesto.objects.all().exclude(pk=self.id).update(es_predet='N')

        super(Impuesto, self).save(*args, **kwargs)  

    def __unicode__(self):
        return self.nombre
        
    class Meta:
        db_table = u'impuestos'


class Registry(models.Model):
    id = models.AutoField(primary_key=True, db_column='ELEMENTO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    padre = models.ForeignKey('self', related_name='padre_a')
    valor = models.CharField(default='', blank = True, null = True, max_length=100, db_column='VALOR')

    def __unicode__(self):
        return u'%s' % self.nombre
    
    def get_value(self):
        if self.valor == '':
            return None
        return self.valor

    class Meta:
        db_table = u'registry'

class CondicionPagoCp(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'condiciones_pago_cp'
        

class CondicionPagoCPPlazo(models.Model):
    id = models.AutoField(primary_key=True, db_column='PLAZO_COND_PAG_ID')
    condicion_de_pago = models.ForeignKey(CondicionPagoCp, db_column='COND_PAGO_ID')
    dias = models.PositiveSmallIntegerField( db_column='DIAS_PLAZO')
    porcentaje_de_venta = models.PositiveSmallIntegerField( db_column='PCTJE_VEN')
    
    def save(self, *args, **kwargs):    
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)

        super(CondicionPagoCPPlazo, self).save(*args, **kwargs)

    class Meta:
        db_table = u'plazos_cond_pag_cp'

class TipoProveedor(models.Model):
    id      = models.AutoField(primary_key=True, db_column='TIPO_PROV_ID')
    nombre  = models.CharField(max_length=30, db_column='NOMBRE')
   
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'tipos_prov'
        
class Proveedor(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PROVEEDOR_ID')
    nombre              = models.CharField(max_length=100, db_column='NOMBRE')
    cuenta_xpagar       = models.CharField(max_length=30, db_column='CUENTA_CXP', blank=True, null=True)
    cuenta_anticipos    = models.CharField(max_length=9, db_column='CUENTA_ANTICIPOS', blank=True, null=True)
    moneda              = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    tipo                = models.ForeignKey(TipoProveedor, db_column='TIPO_PROV_ID')
    rfc_curp            = models.CharField(max_length=18, db_column='RFC_CURP', blank=True, null=True)
    condicion_de_pago   = models.ForeignKey(CondicionPagoCp, db_column='COND_PAGO_ID')
    #Direccion
    pais                = models.ForeignKey(Pais, db_column='PAIS_ID', blank=True, null=True)
    estado              = models.ForeignKey(Estado, db_column='ESTADO_ID', blank=True, null=True)
    ciudad              = models.ForeignKey(Ciudad, db_column='CIUDAD_ID')
    
    TIPOS_OPERACION     = (('03', 'Prestacion de Servicios Profesionales'),('06', 'Arrendamiento de Inmuebles'),('85', 'Otros'),)
    actividad_principal = models.CharField(max_length=3, choices=TIPOS_OPERACION, db_column='ACTIVIDAD_PRINCIPAL', default='85')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'proveedores'

class FoliosFiscales(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIOS_FISCALES_ID')
    serie = models.CharField(max_length=3, db_column='SERIE')
    folio_ini = models.IntegerField(db_column='FOLIO_INI')
    folio_fin = models.IntegerField(db_column='FOLIO_FIN')
    ultimo_utilizado = models.IntegerField(db_column='ULTIMO_UTILIZADO')
    num_aprobacion = models.CharField(max_length=14, db_column='NUM_APROBACION')
    ano_aprobacion = models.IntegerField(db_column='ANO_APROBACION')
    modalidad_facturacion = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    fecha_aprobacion = models.DateField(db_column='FECHA_APROBACION', blank=True, null=True)
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO', blank=True, null=True)
    
    def __str__(self):  
          return u'%s' % self.id    
          
    class Meta:
        db_table =u'folios_fiscales' 

class UsoFoliosFiscales(models.Model):
    id = models.AutoField(primary_key=True, db_column='USO_FOLIO_ID')
    folios_fiscales = models.ForeignKey(FoliosFiscales, db_column='FOLIOS_FISCALES_ID')
    folio = models.IntegerField(db_column='FOLIO')
    fecha = models.DateField(db_column='FECHA')
    sistema = models.CharField(max_length=2, db_column='SISTEMA')
    documento = models.IntegerField(db_column='DOCTO_ID')
    xml = models.TextField(db_column='XML')
    prov_cert = models.CharField(max_length=20, db_column='PROV_CERT')
    fechahora_timbrado = models.CharField(max_length=25, db_column='FECHA_HORA_TIMBRADO')
    uuid = models.CharField(max_length=45, db_column='UUID')
    
    def __str__(self):  
          return u'%s' % self.id    
          
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(UsoFoliosFiscales, self).save(*args, **kwargs)

    class Meta:
        db_table =u'usos_folios_fiscales'

class FolioVenta(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIO_VENTAS_ID')
    tipo_doc = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    serie = models.CharField(max_length=3, db_column='SERIE')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')
    modalidad_facturacion = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    punto_reorden = models.IntegerField(db_column='PUNTO_REORDEN_FOLIOS')
    dias_reorden = models.IntegerField(db_column='DIAS_REORDEN_FOLIOS')
    
    
    def __unicode__(self):
        return u'%s'%self.id
        
    class Meta:
        db_table = u'folios_ventas'

class FolioCompra(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIO_COMPRAS_ID')
    tipo_doc = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    serie = models.CharField(max_length=3, db_column='SERIE')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')
    
    def __unicode__(self):
        return u'%s'%self.id
        
    class Meta:
        db_table = u'folios_compras'

class ActivosFijos(models.Model):
    class Meta:
        db_table = u'activos_fijos'

class AcumCuentasCoTemp(models.Model):
    class Meta:
        db_table = u'acum_cuentas_co_temp'

class Aduana(models.Model):
    id = models.AutoField(primary_key=True, db_column='ADUANA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    ciudad = models.ForeignKey(Ciudad, db_column='CIUDAD_ID')
    gln = models.CharField(blank=True, null=True, max_length=20, db_column='GLN')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'aduanas'

class Agentes(models.Model):
    AGENTE_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'agentes'

class Almacenes(models.Model):
    ALMACEN_ID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')

    inventariando = models.BooleanField(default= False, db_column = 'SIC_INVENTARIANDO' )
    inventario_conajustes = models.BooleanField(default= False, db_column = 'SIC_INVCONAJUSTES' )
    inventario_modifcostos = models.BooleanField(default= False, db_column = 'SIC_INVMODIFCOSTOS' )
    

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'almacenes'

class GrupoLineas(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='GRUPO_LINEA_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    puntos              = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'grupos_lineas'

class LineaArticulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='LINEA_ARTICULO_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    grupo               = models.ForeignKey(GrupoLineas, db_column='GRUPO_LINEA_ID')
    puntos              = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')
    hereda_puntos       = models.BooleanField( db_column='SIC_HEREDA_PUNTOS')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'lineas_articulos'

class Articulos( models.Model ):
    id = models.AutoField( primary_key = True, db_column = 'ARTICULO_ID' )
    nombre = models.CharField( max_length = 100, db_column = 'NOMBRE' )
    es_almacenable = models.CharField( default = 'S', max_length = 1, db_column = 'ES_ALMACENABLE' )
    estatus = models.CharField( default = 'A', max_length = 1, db_column = 'ESTATUS' )
    seguimiento = models.CharField( default = 'N', max_length = 1, db_column = 'SEGUIMIENTO' )
    cuenta_ventas = models.CharField( max_length = 30, blank = True, null = True, db_column = 'CUENTA_VENTAS' )
    linea = models.ForeignKey( LineaArticulos, db_column = 'LINEA_ARTICULO_ID' )
    nota_ventas = models.TextField( db_column = 'NOTAS_VENTAS', blank = True, null = True )
    unidad_venta = models.CharField( default = 'PIEZA', max_length = 20, blank = True, null = True, db_column = 'UNIDAD_VENTA' )
    unidad_compra = models.CharField( default = 'PIEZA' , max_length = 20, blank = True, null = True, db_column = 'UNIDAD_COMPRA' )
    costo_ultima_compra = models.DecimalField( default = 0, blank = True, null = True, max_digits = 18, decimal_places = 6, db_column = 'COSTO_ULTIMA_COMPRA' )

    usuario_ult_modif = models.CharField( blank = True, null = True, max_length = 31, db_column = 'USUARIO_ULT_MODIF' )
    fechahora_ult_modif = models.DateTimeField( auto_now = True, blank = True, null = True, db_column = 'FECHA_HORA_ULT_MODIF' )

    puntos = models.IntegerField(default = 0, blank = True, null = True, db_column = 'SIC_PUNTOS' )
    dinero_electronico  = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_DINERO_ELECTRONICO' )
    hereda_puntos = models.BooleanField( db_column = 'SIC_HEREDA_PUNTOS' )
    carpeta = models.ForeignKey( Carpeta, blank = True, null = True, db_column = 'SIC_CARPETA_ID' )

    def __unicode__( self) :
        return u'%s (%s)' % ( self.nombre, self.unidad_venta )

    class Meta:
        db_table = u'articulos'

class PrecioEmpresa(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PRECIO_EMPRESA_ID')
    nombre              = models.CharField(default='N', max_length=30, db_column='NOMBRE')
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'PRECIOS_EMPRESA'

class PrecioArticulo(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PRECIO_ARTICULO_ID')
    articulo            = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    precio_empresa      = models.ForeignKey(PrecioEmpresa, db_column='PRECIO_EMPRESA_ID')
    precio              = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=6, db_column='PRECIO')
    moneda              = models.ForeignKey(Moneda, db_column='MONEDA_ID')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'precios_articulos'


class ArticulosClientes(models.Model):
    class Meta:
        db_table = u'articulos_clientes'

class ArticulosDiscretos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ART_DISCRETO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE')
    articulo = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.clave
        
    class Meta:
        db_table = u'articulos_discretos'

class ExistDiscreto(models.Model):
    id = models.AutoField(primary_key=True, db_column='EXIS_DISCRETO_ID')
    articulo_discreto = models.ForeignKey(ArticulosDiscretos, db_column='ART_DISCRETO_ID')
    almacen = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    existencia = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='EXISTENCIA')
    
    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'exis_discretos'


class Atributos(models.Model):
    class Meta:
        db_table = u'atributos'

class Bancos(models.Model):
    BANCO_ID = models.AutoField(primary_key=True)
    class Meta:
        db_table = u'bancos'

class Beneficiarios(models.Model):
    BENEFICIARIO_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'beneficiarios'

class Bitacora(models.Model):
    class Meta:
        db_table = u'bitacora'

class BookmarksReportes(models.Model):
    class Meta:
        db_table = u'bookmarks_reportes'

class CajasCajeros(models.Model):
    class Meta:
        db_table = u'cajas_cajeros'

class CapasCostos(models.Model):
    class Meta:
        db_table = u'capas_costos'

class ViaEmbarque(models.Model):
    id = models.AutoField(primary_key=True, db_column='VIA_EMBARQUE_ID')
    nombre = models.CharField(max_length=20, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'vias_embarque'

class Pedimento(models.Model):
    id = models.AutoField(primary_key=True, db_column='PEDIMENTO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE')
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)
    aduana_nombre = models.CharField(max_length=50, db_column='ADUANA')
    aduana = models.ForeignKey(Aduana, db_column='ADUANA_ID')

    class Meta:
        db_table = u'pedimentos'

class CapasPedimentos(models.Model):
    class Meta:
        db_table = u'capas_pedimentos'

class CargosPeriodicosCc(models.Model):
    class Meta:
        db_table = u'cargos_periodicos_cc'

class CentrosCosto(models.Model):
    id = models.AutoField(primary_key=True, db_column='CENTRO_COSTO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')
    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    def __unicode__(self):
        return self.nombre 
    class Meta:
        db_table = u'centros_costo'

class CertCfdProv(models.Model):
    class Meta:
        db_table = u'cert_cfd_prov'

class CfdRecibidos(models.Model):
    class Meta:
        db_table = u'cfd_recibidos'



class RolesClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ROL_CLAVE_ART_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'roles_claves_articulos'

class ClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLAVE_ARTICULO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE_ARTICULO')
    articulo = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    rol = models.ForeignKey(RolesClavesArticulos, db_column='ROL_CLAVE_ART_ID')

    def __unicode__(self):
        return u'%s' % self.clave

    class Meta:
        db_table = u'claves_articulos'

class ClavesCatSec(models.Model):
    class Meta:
        db_table = u'claves_cat_sec'

class ClavesEmpleados(models.Model):
    class Meta:
        db_table = u'claves_empleados'

class Cobradores(models.Model):
    class Meta:
        db_table = u'cobradores'

class ComandosDispositivos(models.Model):
    class Meta:
        db_table = u'comandos_dispositivos'

class ComandosTiposDispositivos(models.Model):
    class Meta:
        db_table = u'comandos_tipos_dispositivos'

class ComisCobTipoCli(models.Model):
    class Meta:
        db_table = u'comis_cob_tipo_cli'

class ComisCobZona(models.Model):
    class Meta:
        db_table = u'comis_cob_zona'

class ComisVenArt(models.Model):
    class Meta:
        db_table = u'comis_ven_art'

class ComisVenCli(models.Model):
    class Meta:
        db_table = u'comis_ven_cli'

class ComisVenGrupo(models.Model):
    class Meta:
        db_table = u'comis_ven_grupo'

class ComisVenLinea(models.Model):
    class Meta:
        db_table = u'comis_ven_linea'

class ComisVenTipoCli(models.Model):
    class Meta:
        db_table = u'comis_ven_tipo_cli'

class ComisVenZona(models.Model):
    class Meta:
        db_table = u'comis_ven_zona'

class CompromArticulos(models.Model):
    class Meta:
        db_table = u'comprom_articulos'

class ConceptosBa(models.Model):
    class Meta:
        db_table = u'conceptos_ba'

class ConceptosDim(models.Model):
    class Meta:
        db_table = u'conceptos_dim'

class ConceptosEmp(models.Model):
    class Meta:
        db_table = u'conceptos_emp'

class ConceptosIn(models.Model):
    id = models.AutoField( primary_key = True, db_column= 'CONCEPTO_IN_ID' )
    nombre_abrev = models.CharField( max_length = 30, db_column = 'NOMBRE_ABREV' )
    naturaleza = models.CharField(max_length=1, db_column='NATURALEZA')
    folio_autom = models.CharField( default = 'N', max_length = 1, db_column = 'FOLIO_AUTOM' )
    sig_folio = models.CharField( max_length = 9, db_column = 'SIG_FOLIO' )

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_in'

class ConceptosNo(models.Model):
    class Meta:
        db_table = u'conceptos_no'

class CondicionPago(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')

    def __unicode__(self):
        return self.nombre
    class Meta:
        db_table = u'condiciones_pago'

class ConfTicketsCajas(models.Model):
    class Meta:
        db_table = u'conf_tickets_cajas'

class ConfTicketsCajasPrns(models.Model):
    class Meta:
        db_table = u'conf_tickets_cajas_prns'

class ConsignatarioCompras(models.Model):
    id = models.AutoField(primary_key=True, db_column='CONSIG_CM_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')

    calle = models.CharField(blank=True, null=True, max_length=430, db_column='CALLE')
    calle_nombre = models.CharField(blank=True, null=True, max_length=100, db_column='NOMBRE_CALLE')
    numero_exterior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_EXTERIOR')
    numero_interior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_INTERIOR')
    colonia = models.CharField(blank=True, null=True, max_length=100, db_column='COLONIA')
    poblacion = models.CharField(blank=True, null=True, max_length=100, db_column='POBLACION')
    referencia = models.CharField(blank=True, null=True, max_length=100, db_column='REFERENCIA')
    ciudad = models.ForeignKey(Ciudad, db_column='CIUDAD_ID')
    estado = models.ForeignKey(Estado, db_column='ESTADO_ID', blank=True, null=True)
    codigo_postal = models.CharField(blank=True, null=True, max_length=10, db_column='CODIGO_POSTAL')
    pais = models.ForeignKey(Pais, db_column='PAIS_ID', blank=True, null=True)

    telefono1 = models.CharField(blank=True, null=True, max_length=10, db_column='TELEFONO1')
    telefono2 = models.CharField(blank=True, null=True, max_length=10, db_column='TELEFONO2')
    fax = models.CharField(blank=True, null=True, max_length=10, db_column='FAX')
    email = models.CharField(blank=True, null=True, max_length=200, db_column='EMAIL')
    contacto = models.CharField(blank=True, null=True, max_length=200, db_column='CONTACTO')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'consignatarios_cm'

class CuentasBancarias(models.Model):
    class Meta:
        db_table = u'cuentas_bancarias'

class CuentaCo(models.Model):
    id              = models.AutoField(primary_key=True, db_column='CUENTA_ID')
    nombre          = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta          = models.CharField(max_length=50, db_column='CUENTA_PT')
    tipo            = models.CharField(max_length=1, db_column='TIPO')
    cuenta_padre    = models.IntegerField(db_column='CUENTA_PADRE_ID')
    
    def __unicode__(self):
        return u'%s (%s)' % (self.cuenta, self.nombre)
    class Meta:
        db_table = u'cuentas_co'

class CuentasNo(models.Model):
    class Meta:
        db_table = u'cuentas_no'

class DeptoCo(models.Model):
    id = models.AutoField(primary_key=True, db_column='DEPTO_CO_ID')
    clave = models.CharField(max_length=1, db_column='CLAVE')

    def __unicode__(self):
        return u'%s' % self.clave

    class Meta:
        db_table = u'deptos_co'

class DeptosNo(models.Model):
    class Meta:
        db_table = u'deptos_no'

class DescripPolizas(models.Model):
    class Meta:
        db_table = u'descrip_polizas'

class Dispositivos(models.Model):
    class Meta:
        db_table = u'dispositivos'

class DispositivosCajas(models.Model):
    class Meta:
        db_table = u'dispositivos_cajas'

class DoctosBa(models.Model):
    class Meta:
        db_table = u'doctos_ba'

class DocumentoCompras(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_ID')
    tipo = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    subtipo = models.CharField(blank=True, null=True, max_length=1, db_column='SUBTIPO_DOCTO')
    folio = models.CharField(max_length=9, db_column='FOLIO')
    fecha = models.DateField(default=datetime.now, db_column='FECHA')
    
    proveedor_clave = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_PROV')
    proveedor = models.ForeignKey(Proveedor, db_column='PROVEEDOR_ID')
    proveedor_folio = models.CharField(blank=True, null=True, max_length=9, db_column='FOLIO_PROV')
    factura_dev = models.CharField(blank=True, null=True, max_length=9, db_column='FACTURA_DEV')
    consignatario = models.ForeignKey(ConsignatarioCompras, blank=True, null=True, db_column='CONSIG_CM_ID')
    almacen = models.ForeignKey(Almacenes, default=lambda: firstALMACENid_or_none(Almacenes.objects.filter(es_predet='S')), db_column='ALMACEN_ID')
    pedimento = models.ForeignKey(Pedimento, blank=True, null=True, db_column='PEDIMENTO_ID')
    moneda = models.ForeignKey(Moneda, default=lambda:firstid_or_none(Moneda.objects.filter(es_predet='S')), db_column='MONEDA_ID')
    tipo_cambio = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    
    tipo_descuento = models.CharField(default='P',max_length=1, db_column='TIPO_DSCTO')
    porcentaje_descuento = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='DSCTO_PCTJE')
    importe_descuento = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='DSCTO_IMPORTE')
    
    estado = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    aplicado = models.CharField(default='S', max_length=1, db_column='APLICADO')
    fecha_entrega = models.DateField(blank=True, null=True, db_column='FECHA_ENTREGA')
    descripcion = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    importe_neto = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    fletes = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='FLETES')
    otros_cargos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='OTROS_CARGOS')
    total_impuestos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')
    total_retenciones = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_RETENCIONES')
    gastos_aduanales = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='GASTOS_ADUANALES')
    otros_gastos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='OTROS_GASTOS')
    total_fpgc = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_FPGC')

    forma_emitida = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='FORMA_EMITIDA')
    contabilizado = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    acreditar_cxp = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='ACREDITAR_CXP')
    sistema_origen = models.CharField(default='CM', max_length=2, db_column='SISTEMA_ORIGEN')
    condicion_pago = models.ForeignKey(CondicionPagoCp, db_column='COND_PAGO_ID')
    fecha_dscto_ppag = models.DateField(blank=True, null=True, db_column='FECHA_dscto_ppag')
    porcentaje_dscto_ppag = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PPAG')
    via_embarque = models.ForeignKey(ViaEmbarque, blank=True, null=True, db_column='VIA_EMBARQUE_ID')
    impuesto_sustituido = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID', related_name='impuesto_sustituidoID')
    impuesto_sustituto = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID', related_name='impuesto_sustitutoID')
    cargar_sun = models.CharField(default='S', max_length=1, db_column='CARGAR_SUN')
    enviado = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    envio_fechahora = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ENVIO')
    envio_email = models.EmailField(blank=True, null=True, db_column='EMAIL_ENVIO')
    tiene_cfd = models.CharField(default='N', max_length=1, db_column='TIENE_CFD')

    usuario_creador = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    usuario_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
    
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

        super(DocumentoCompras, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'doctos_cm'

class VencimientoCargoCompra(models.Model):
    

    documento = models.ForeignKey(DocumentoCompras, unique_for_date='fecha', db_column='DOCTO_CM_ID')
    fecha = models.DateField(db_column='FECHA_VENCIMIENTO') 
    porcentaje_de_venta = models.PositiveSmallIntegerField( db_column='PCTJE_VEN')

    class Meta:
        db_table = u'vencimientos_cargos_cm'

class DocumentoComprasDetalle(models.Model):


    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_DET_ID')
    documento = models.ForeignKey(DocumentoCompras, db_column='DOCTO_CM_ID')

    clave_articulo = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    unidades_rec_dev = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='UNIDADES_REC_DEV')
    unidades_a_rec = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='UNIDADES_A_REC')
    umed = models.CharField(blank=True, null=True, max_length=20, db_column='UMED')
    contenido_umed = models.DecimalField(default=1, max_digits=18, decimal_places=5, db_column='CONTENIDO_UMED')
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    fpgc_unitario = models.DecimalField(default=0, max_digits=18, decimal_places=6, db_column='FPGC_UNITARIO')
    porcentaje_descuento = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    porcentaje_descuento_pro = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PRO')
    porcentaje_descuento_vol = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_VOL')
    porcentaje_descuento_promo = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PROMO')
    precio_total_neto = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')

    porcentaje_arancel = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='PCTJE_ARANCEL')
    notas = models.TextField(blank=True, null=True, db_column='NOTAS')
    posicion = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(DocumentoComprasDetalle, self).save(*args, **kwargs)
        
    class Meta:
        db_table = u'doctos_cm_det'

class DocumentoComprasLiga(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_LIGA_ID')
    documento_fte = models.ForeignKey(DocumentoCompras, related_name='fuente', db_column='DOCTO_CM_FTE_ID')  
    documento_dest = models.ForeignKey(DocumentoCompras, related_name='destino', db_column='DOCTO_CM_DEST_ID')  

    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(DocumentoComprasLiga, self).save(*args, **kwargs)

    class Meta:
        db_table = u'doctos_cm_ligas'

class DocumentoComprasImpuestoManager(models.Manager):
    def get_by_natural_key(self, documento,  impuesto):
        return self.get(documento= documento, impuesto= impuesto,)

class DocumentoComprasImpuesto(models.Model):
    objects = DocumentoComprasImpuestoManager()

    documento = models.ForeignKey(DocumentoCompras, db_column='DOCTO_CM_ID')
    impuesto = models.ForeignKey(Impuesto, db_column='IMPUESTO_ID')
    compra_neta = models.DecimalField(max_digits=15, decimal_places=2, db_column='COMPRA_NETA')
    otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')
    importe_impuesto = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_cm'
        unique_together = (('documento', 'impuesto',),)

class DocumentoComprasDetalleLigaManager(models.Manager):
    def get_by_natural_key(self, documento_liga,  detalle_fuente, detalle_destino):
        return self.get(documento_liga=documento_liga, detalle_fuente=detalle_fuente, detalle_destino=detalle_destino,)

class DocumentoComprasDetalleLiga(models.Model):
    objects = DocumentoComprasDetalleLigaManager()
    documento_liga = models.ForeignKey(DocumentoComprasLiga, related_name='liga', db_column='DOCTO_CM_LIGA_ID')
    detalle_fuente = models.ForeignKey(DocumentoComprasDetalle, related_name='fuente', db_column='DOCTO_CM_DET_FTE_ID')
    detalle_destino = models.ForeignKey(DocumentoComprasDetalle, related_name='destino', db_column='DOCTO_CM_DET_DEST_ID')

    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )

    class Meta:
        db_table = u'doctos_cm_ligas_det'
        unique_together = (('documento_liga', 'detalle_fuente','detalle_destino',),)
        
class DoctosCmProeve(models.Model):
    class Meta:
        db_table = u'doctos_cm_proeve'

##########################################
##                                      ##
##                POLIZAS               ##
##                                      ##
##########################################
class Recordatorio(models.Model):
    id = models.AutoField(primary_key=True, db_column='RECORDATORIO_ID')
    
    class Meta:
        db_table = u'recordatorios'

class GrupoPolizasPeriodoCo(models.Model):
    id = models.AutoField(primary_key=True, db_column='GRUPO_POL_PERIOD_ID')

    class Meta:
        db_table = 'grupos_polizas_period_co'

class DoctosEntreSis(models.Model):
    class Meta:
        db_table = u'doctos_entre_sis'

# def my_handler(sender, instance=False, **kwargs):
    
#     t = DoctosIn.objects.get(id=instance.id)
#     t.aplicado = 'S'
#     t.save()

class DoctosIn(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_IN_ID')
    folio               = models.CharField(max_length=50, db_column='FOLIO')
    almacen             = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    concepto            = models.ForeignKey(ConceptosIn, db_column='CONCEPTO_IN_ID')
    naturaleza_concepto = models.CharField(default='S', max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(db_column='FECHA') 
    cancelado           = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S',blank=True, null=True, max_length=1, db_column='APLICADO')
    forma_emitida       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='FORMA_EMITIDA')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    sistema_origen      = models.CharField(default='IN', max_length=2, db_column='SISTEMA_ORIGEN')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')

    class Meta:
        db_table = u'doctos_in'

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

        super(DoctosIn, self).save(*args, **kwargs)

# post_init.connect(my_handler, sender=DoctosIn)

class DoctosInvfis(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_INVFIS_ID')
    almacen             = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    fecha               = models.DateField(db_column='FECHA') 
    cancelado           = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='N',blank=True, null=True, max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion= models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'doctos_invfis'

class DoctosInvfisDet(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_INVFIS_DET_ID')
    docto_invfis= models.ForeignKey(DoctosInvfis, db_column='DOCTO_INVFIS_ID')
    clave       = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo    = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    unidades    = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='UNIDADES')
    # fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='SIC_FECHAHORA_U')
    # usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='SIC_USUARIO_ULT_MODIF')
    # detalle_modificaciones = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLE_MODIFICACIONES')
    # detalle_modificacionestime = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLETIME_MODIFICACIONES')
    # unidades_syn = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='SIC_UNIDADES_SYN')
    # unidades_margen = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='SIC_UNIDADESMARGEN')
    
    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_invfis_det'

class DoctosInDet(models.Model):
    id              = models.AutoField(primary_key=True, db_column='DOCTO_IN_DET_ID')
    doctosIn        = models.ForeignKey(DoctosIn, db_column='DOCTO_IN_ID')
    almacen         = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    concepto        = models.ForeignKey(ConceptosIn, db_column='CONCEPTO_IN_ID')
    claveArticulo   = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo        = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    tipo_movto      = models.CharField(default='E', max_length=1, db_column='TIPO_MOVTO')
    unidades        = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='UNIDADES')
    costo_unitario  = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='COSTO_UNITARIO')
    costo_total     = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='COSTO_TOTAL')
    metodo_costeo   = models.CharField(default='C', max_length=1, db_column='METODO_COSTEO')
    cancelado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado        = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='APLICADO')
    costeo_pend     = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='COSTEO_PEND')
    pedimento_pend  = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='PEDIMENTO_PEND')
    rol             = models.CharField(default='N', max_length=1, db_column='ROL')
    fecha           = models.DateField(auto_now=True, blank=True, null=True, db_column='FECHA')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='SIC_FECHAHORA_U')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='SIC_USUARIO_ULT_MODIF')
    detalle_modificacionestime = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLETIME_MODIFICACIONES')
    
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(DoctosInDet, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_in_det'

class DesgloseEnDiscretos(models.Model):
    id = models.AutoField(primary_key=True, db_column='DESGLOSE_DISCRETO_ID')
    docto_in_det = models.ForeignKey(DoctosInDet, db_column='DOCTO_IN_DET_ID')
    art_discreto = models.ForeignKey(ArticulosDiscretos, db_column='ART_DISCRETO_ID')
    unidades = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'desglose_en_discretos'

class DesgloseEnDiscretosCm(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_cm'

class DesgloseEnDiscretosInvfis(models.Model):
    id = models.AutoField(primary_key=True, db_column='DESGL_DISCRETO_INVFIS_ID')
    docto_invfis_det = models.ForeignKey(DoctosInvfisDet, db_column='DOCTO_INVFIS_DET_ID')
    art_discreto = models.ForeignKey(ArticulosDiscretos, db_column='ART_DISCRETO_ID')
    unidades = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')
    
    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'desglose_en_discretos_invfis'

class DesgloseEnDiscretosPv(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_pv'

class DesgloseEnDiscretosVe(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_ve'

class DesgloseEnPedimentos(models.Model):
    class Meta:
        db_table = u'desglose_en_pedimentos'
        
#######################################################VENTAS###############################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
class Vendedor(models.Model):
    id              = models.AutoField(primary_key=True, db_column='VENDEDOR_ID')
    nombre          = models.CharField(max_length=50, db_column='NOMBRE')
    

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'vendedores'
################################################################
####                                                        ####
####                    MODELOS CLIENTES                    ####
####                                                        ####
################################################################

class TipoCliente( models.Model ):
    id              = models.AutoField( primary_key = True, db_column = 'TIPO_CLIENTE_ID' )
    nombre          = models.CharField( max_length = 100, db_column = 'NOMBRE' )
    valor_puntos    = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_VALOR_PUNTOS' )

    def __unicode__( self ):
        return self.nombre
        
    class Meta:
        db_table = u'tipos_clientes'

class Cliente( models.Model ):
    id = models.AutoField( primary_key = True, db_column = 'CLIENTE_ID' )
    nombre = models.CharField( max_length = 100, db_column = 'NOMBRE' )
    estatus = models.CharField( default = 'A',  max_length = 1, db_column = 'ESTATUS' )
    cuenta_xcobrar = models.CharField( max_length = 9, db_column = 'CUENTA_CXC' )
    tipo_cliente = models.ForeignKey( TipoCliente, db_column = 'TIPO_CLIENTE_ID' )
    usuario_ult_modif = models.CharField( blank = True, null = True, max_length = 31, db_column = 'USUARIO_ULT_MODIF' )
    fechahora_ult_modif = models.DateTimeField( auto_now = True, blank = True, null = True, db_column = 'FECHA_HORA_ULT_MODIF' )
    moneda = models.ForeignKey(Moneda, db_column = 'MONEDA_ID' )
    condicion_de_pago = models.ForeignKey(CondicionPago, db_column='COND_PAGO_ID')
    
    TIPOS = ( ( 'N', 'No Aplica' ),( 'P', 'Puntos' ),( 'D', 'Dinero Electronico' ), )
    puntos = models.IntegerField( db_column = 'SIC_PUNTOS' )
    dinero_electronico = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_DINERO_ELECTRONICO' )
    tipo_tarjeta = models.CharField( default = 'N', max_length = 1, choices = TIPOS, db_column = 'SIC_TIPO_TARJETA' )
    hereda_valorpuntos = models.BooleanField( db_column = 'SIC_HEREDA_VALORPUNTOS' )
    valor_puntos = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2, db_column = 'SIC_VALOR_PUNTOS' )
    hereda_puntos_a = models.ForeignKey( 'self', db_column = 'SIC_HEREDAR_PUNTOS_A', related_name = 'hereda_puntos_a_cliente', blank = True, null = True )
    # cuenta_1 = models.ForeignKey(CuentaCo, db_column='CUENTA_1', blank=True, null=True, related_name='cuenta_1')
    # cuenta_2 = models.ForeignKey(CuentaCo, db_column='CUENTA_2', blank=True, null=True, related_name='cuenta_2')
    # cuenta_3 = models.ForeignKey(CuentaCo, db_column='CUENTA_3', blank=True, null=True, related_name='cuenta_3')
    # cuenta_4 = models.ForeignKey(CuentaCo, db_column='CUENTA_4', blank=True, null=True, related_name='cuenta_4')
    # cuenta_5 = models.ForeignKey(CuentaCo, db_column='CUENTA_5', blank=True, null=True, related_name='cuenta_5')


    def __unicode__( self ):
        return self.nombre

    class Meta:
        db_table = u'clientes'

class RolClavesClientes(models.Model):
    id      = models.AutoField(primary_key=True, db_column='ROL_CLAVE_CLI_ID')
    nombre  = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    class Meta:
        db_table = u'roles_claves_clientes'

class ClavesClientes(models.Model):
    id      = models.AutoField(primary_key=True, db_column='CLAVE_CLIENTE_ID')
    clave   = models.CharField(max_length=20, db_column='CLAVE_CLIENTE')
    cliente = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    rol     = models.ForeignKey(RolClavesClientes, db_column='ROL_CLAVE_CLI_ID')
    
    def __unicode__(self):
        return self.clave

    class Meta:
        db_table = u'claves_clientes'

class DirCliente(models.Model):
    id = models.AutoField(primary_key=True, db_column='DIR_CLI_ID')
    cliente = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    rfc_curp = models.CharField(max_length=18, db_column='RFC_CURP')

    class Meta:
        db_table = u'dirs_clientes'

class libresClientes(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLIENTE_ID')
    heredar_puntos_a = models.CharField(max_length=99, db_column='HEREDAR_PUNTOS_A')
    cuenta_1 = models.CharField(max_length=99, db_column='CUENTA_1')
    cuenta_2 = models.CharField(max_length=99, db_column='CUENTA_2')
    cuenta_3 = models.CharField(max_length=99, db_column='CUENTA_3')
    cuenta_4 = models.CharField(max_length=99, db_column='CUENTA_4')
    cuenta_5 = models.CharField(max_length=99, db_column='CUENTA_5')
    
    class Meta:
        db_table = u'libres_clientes'



class ImpuestosArticulo(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPUESTO_ART_ID')
    articulo    = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto    = models.ForeignKey(Impuesto, db_column='IMPUESTO_ID')

    def __unicode__(self):
        return self.impuesto

    class Meta:
        db_table = u'impuestos_articulos'

################################################################
####                                                        ####
####               MODELOS CUENTAS POR PAGAR                ####
####                                                        ####
################################################################


class ClavesProveedores(models.Model):    
    class Meta:
        db_table = u'claves_proveedores'


class ConceptoCp(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='CONCEPTO_CP_ID')
    nombre_abrev        = models.CharField(max_length=30, db_column='NOMBRE_ABREV')
    crear_polizas       = models.CharField(default='N', max_length=1, db_column='CREAR_POLIZAS')
    cuenta_contable     = models.CharField(max_length=30, db_column='CUENTA_CONTABLE')
    clave_tipo_poliza   = models.CharField(max_length=1, db_column='TIPO_POLIZA')
    descripcion_poliza  = models.CharField(max_length=200, db_column='DESCRIPCION_POLIZA')

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_cp'

class DoctosCp(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
    concepto            = models.ForeignKey(ConceptoCp, db_column='CONCEPTO_CP_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    naturaleza_concepto = models.CharField(max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(db_column='FECHA') 
    proveedor           = models.ForeignKey(Proveedor, db_column='PROVEEDOR_ID')
    cancelado           = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S', max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    condicion_pago      = models.ForeignKey(CondicionPagoCp, db_column='COND_PAGO_ID')

    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'doctos_cp'

class ImportesDoctosCP(models.Model):
    id              = models.AutoField(primary_key=True, db_column='IMPTE_DOCTO_CP_ID')
    docto_cp        = models.ForeignKey(DoctosCp, db_column='DOCTO_CP_ID')
    importe         = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPUESTO')
    iva_retenido    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IVA_RETENIDO')
    isr_retenido    = models.DecimalField(max_digits=15, decimal_places=2, db_column='ISR_RETENIDO')
    dscto_ppag      = models.DecimalField(max_digits=15, decimal_places=2, db_column='DSCTO_PPAG')
    cancelado       = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    
    class Meta:
        db_table = u'importes_doctos_cp'

class LibresCargosCP(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'libres_cargos_cp'


################################################################
####                                                        ####
####               MODELOS CUENTAS POR COBRAR               ####
####                                                        ####
################################################################


class ConceptoCc(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='CONCEPTO_CC_ID')
    nombre_abrev        = models.CharField(max_length=30, db_column='NOMBRE_ABREV')
    crear_polizas       = models.CharField(default='N', max_length=1, db_column='CREAR_POLIZAS')
    cuenta_contable     = models.CharField(max_length=30, db_column='CUENTA_CONTABLE')
    clave_tipo_poliza   = models.CharField(max_length=1, db_column='TIPO_POLIZA')
    descripcion_poliza  = models.CharField(max_length=200, db_column='DESCRIPCION_POLIZA')
    tipo                = models.CharField(max_length=1, db_column='TIPO')

    def __unicode__(self):
        return self.nombre_abrev

    class Meta:
        db_table = u'conceptos_cc'

class DoctosCc(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_CC_ID')
    concepto            = models.ForeignKey(ConceptoCc, db_column='CONCEPTO_CC_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    naturaleza_concepto = models.CharField(max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(db_column='FECHA') 
    cliente             = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    cancelado           = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='S', max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    contabilizado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    condicion_pago      = models.ForeignKey(CondicionPago, db_column='COND_PAGO_ID')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_cc'

class ImportesDoctosCC(models.Model):
    id              = models.AutoField(primary_key=True, db_column='IMPTE_DOCTO_CC_ID')
    docto_cc        = models.ForeignKey(DoctosCc, db_column='DOCTO_CC_ID')
    importe         = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPUESTO')
    iva_retenido    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IVA_RETENIDO')
    isr_retenido    = models.DecimalField(max_digits=15, decimal_places=2, db_column='ISR_RETENIDO')
    dscto_ppag      = models.DecimalField(max_digits=15, decimal_places=2, db_column='DSCTO_PPAG')
    cancelado       = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    
    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'importes_doctos_cc'

class LibresCargosCC(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_CC_ID')
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'libres_cargos_cc'

class LibresCreditosCC(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_CC_ID')
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'libres_creditos_cc'

################################################################
####                                                        ####
####               MODELOS CONTABILIDAD                     ####
####                                                        ####
################################################################

class TipoPoliza(models.Model):
    id          = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_ID')
    clave       = models.CharField(max_length=1, db_column='CLAVE')
    nombre      = models.CharField(max_length=30, db_column='NOMBRE')
    tipo_consec = models.CharField(max_length=1, db_column='TIPO_CONSEC')
    prefijo     = models.CharField(max_length=1, db_column='PREFIJO')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'tipos_polizas'

class TipoPolizaDet(models.Model):
    id              = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_DET_ID')
    tipo_poliza     = models.ForeignKey(TipoPoliza, db_column='TIPO_POLIZA_ID')
    ano         = models.SmallIntegerField(db_column='ANO')
    mes         = models.SmallIntegerField(db_column='MES')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')

    def __unicode__(self):
        return u'%s' % self.id
        
    class Meta:
        db_table = u'tipos_polizas_det'

class DoctoCo(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_CO_ID')
    tipo_poliza             = models.ForeignKey(TipoPoliza, db_column='TIPO_POLIZA_ID')
    poliza                  = models.CharField(max_length=9, db_column='POLIZA')
    fecha                   = models.DateField(db_column='FECHA')
    moneda                  = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estatus                 = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    cancelado               = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    ajuste                  = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    integ_co                = models.CharField(default='S', max_length=1, db_column='INTEG_CO')
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    forma_emitida           = models.CharField(default='N', max_length=1, db_column='FORMA_EMITIDA')
    sistema_origen          = models.CharField(max_length=2, db_column='SISTEMA_ORIGEN')
    nombre                  = models.CharField(blank=True, null=True, max_length=30, db_column='NOMBRE')
    grupo_poliza_periodo    = models.ForeignKey(GrupoPolizasPeriodoCo, blank=True, null=True, db_column='GRUPO_POL_PERIOD_ID')
    integ_ba                = models.CharField(default='N', max_length=1, db_column='INTEG_BA')
    
    usuario_creador         = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_co'

class DoctosCoDet(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_CO_DET_ID')
    docto_co    = models.ForeignKey(DoctoCo, db_column='DOCTO_CO_ID')
    cuenta      = models.ForeignKey(CuentaCo, db_column='CUENTA_ID')
    depto_co    = models.ForeignKey(DeptoCo, db_column='DEPTO_CO_ID')
    tipo_asiento= models.CharField(default='C', max_length=1, db_column='TIPO_ASIENTO')
    importe     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    importe_mn  = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_MN')
    ref         = models.CharField(max_length=10, db_column='REFER')
    descripcion = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    posicion    = models.IntegerField(default=0)
    recordatorio= models.ForeignKey(Recordatorio, blank=True, null=True, db_column='RECORDATORIO_ID')
    fecha       = models.DateField(db_column='FECHA')
    cancelado   = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado    = models.CharField(default='N', max_length=1, db_column='APLICADO')
    ajuste      = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    moneda      = models.ForeignKey(Moneda, db_column='MONEDA_ID')

    class Meta:
        db_table = u'doctos_co_det'


################################################################
####                                                        ####
####               MODELOS PUNTO DE VENTA                   ####
####                                                        ####
################################################################

class Cajero(models.Model):
    id          = models.AutoField(primary_key=True, db_column='CAJERO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    usuario     = models.CharField(max_length=31, db_column='USUARIO')

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'cajeros'

class Caja(models.Model):
    id              = models.AutoField(primary_key=True, db_column='CAJA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    
    def __unicode__(self):
        return self.nombre 

    class Meta:
        db_table = u'cajas'

#Documentos
class Docto_PV(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_PV_ID')
    caja                    = models.ForeignKey(Caja, db_column='CAJA_ID')
    tipo                    = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    folio                   = models.CharField(max_length=9, db_column='FOLIO')
    fecha                   = models.DateField(db_column='FECHA')
    hora                    = models.TimeField(db_column='HORA')
    cajero                  = models.ForeignKey(Cajero, db_column='CAJERO_ID')
    clave_cliente           = models.CharField(max_length=20, db_column='CLAVE_CLIENTE')
    cliente                 = models.ForeignKey(Cliente, db_column='CLIENTE_ID', related_name='cliente')
    clave_cliente_fac       = models.CharField(max_length=20, db_column='CLAVE_CLIENTE_FAC')
    cliente_fac             = models.ForeignKey(Cliente, db_column='CLIENTE_FAC_ID', related_name='cliente_factura')
    direccion_cliente       = models.ForeignKey(DirCliente, db_column='DIR_CLI_ID')
    almacen                 = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    moneda                  = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    impuesto_incluido       = models.CharField(default='S', max_length=1, db_column='IMPUESTO_INCLUIDO')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    tipo_descuento          = models.CharField(default='P',max_length=1, db_column='TIPO_DSCTO')
    porcentaje_descuento    = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='DSCTO_PCTJE')
    importe_descuento       = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='DSCTO_IMPORTE')
    estado                  = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    importe_neto            = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos         = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')

    importe_donativo        = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_DONATIVO')
    total_fpgc              = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_FPGC')
        
    ticket_emitido          = models.CharField(default='N', max_length=1, db_column='TICKET_EMITIDO')
    forma_emitida           = models.CharField(default='N', max_length=1, db_column='FORMA_EMITIDA')
    forma_global_emitida    = models.CharField(default='N', max_length=1, db_column='FORMA_GLOBAL_EMITIDA')
    contabilizado           = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')

    sistema_origen          = models.CharField(default='PV', max_length=2, db_column='SISTEMA_ORIGEN')
    vendedor                = models.ForeignKey(Vendedor, db_column='VENDEDOR_ID')
    cargar_sun              = models.CharField(default='S', max_length=1, db_column='CARGAR_SUN')
    persona                 = models.CharField(max_length=50, db_column='PERSONA')
    refer_reting            = models.CharField(blank=True, null=True, max_length=50, db_column='REFER_RETING')
    unidad_comprom          = models.CharField(default='N', max_length=1, db_column='UNID_COMPROM')    
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    
    impuesto_sustituido     = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID', related_name='impuesto_sustituido')
    impuesto_sustituto      = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID', related_name='impuesto_sustituto')
    
    es_cfd                  = models.CharField(default='N', max_length=1, db_column='ES_CFD')
    modalidad_facturacion   = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    enviado                 = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    email_envio             = models.EmailField(blank=True, null=True, db_column='EMAIL_ENVIO')
    fecha_envio             = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ENVIO')

    #Factura global
    # tipo_gen_fac = models.CharField(default='N',blank=True, null=True, max_length=1, db_column='TIPO_GEN_FAC')
    # es_fac_global = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='ES_FAC_GLOBAL')
    # fecha_ini_fac_global = models.DateField(blank=True, null=True, db_column='FECHA_INI_FAC_GLOBAL')
    # fecha_fin_fac_global = models.DateField(blank=True, null=True, db_column='FECHA_FIN_FAC_GLOBAL')
    
    usuario_creador         = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
    
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
                folios_fiscales = first_or_none(FoliosFiscales.objects.filter(modalidad_facturacion=self.modalidad_facturacion))
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

        super(Docto_PV, self).save(*args, **kwargs)

    class Meta:
        db_table = u'doctos_pv'



#Detalles de documentos
class Docto_pv_det(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_PV_DET_ID')
    documento_pv            = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    clave_articulo          = models.CharField(max_length=20, db_column='CLAVE_ARTICULO')
    articulo                = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades                = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    unidades_dev            = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES_DEV')
    precio_unitario         = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    precio_unitario_impto   = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO_IMPTO')
    fpgc_unitario           = models.DecimalField(max_digits=18, decimal_places=6, db_column='FPGC_UNITARIO')
    porcentaje_descuento    = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto       = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')
    precio_modificado       = models.CharField(default='N', max_length=1, db_column='PRECIO_MODIFICADO')
    vendedor                = models.ForeignKey(Vendedor, blank=True, null=True, db_column='VENDEDOR_ID')
    porcentaje_comis        = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_COMIS')
    rol                     = models.CharField(max_length=1, db_column='ROL')
    notas                   = models.TextField(blank=True, null=True, db_column='NOTAS')
    es_tran_elect           = models.CharField(default='N', max_length=1, db_column='ES_TRAN_ELECT')
    estatus_tran_elect      = models.CharField(max_length=1,blank=True, null=True, db_column='ESTATUS_TRAN_ELECT')
    posicion                =  models.IntegerField(db_column='POSICION')
    puntos                  = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico      = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')

    def __unicode__(self):
        return u'%s(%s)'% (self.id, self.documento_pv)
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_DOCTOS', using)

        super(Docto_pv_det, self).save(*args, **kwargs)    

    class Meta:
        db_table = u'doctos_pv_det'

class DoctoPVLiga(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_PV_LIGA_ID')
    docto_pv_fuente = models.ForeignKey(Docto_PV, related_name='fuente', db_column='DOCTO_PV_FTE_ID')
    docto_pv_destino = models.ForeignKey(Docto_PV, related_name='destino', db_column='DOCTO_PV_DEST_ID')

    def __unicode__(self):
        return u'%s'% self.id 
    
    def save(self, *args, **kwargs):
        
        if self.id == -1:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_LIGAS_DOCTOS', using)

        super(DoctoPVLiga, self).save(*args, **kwargs)

    class Meta:
        db_table = u'doctos_pv_ligas'

class DoctoPVLigaDetManager(models.Manager):
    def get_by_natural_key(self, documento_liga,  detalle_fuente, detalle_destino):
        return self.get(documento_liga=documento_liga, detalle_fuente=detalle_fuente, detalle_destino=detalle_destino,)

class DoctoPVLigaDet(models.Model):
    objects = DoctoPVLigaDetManager()
    documento_liga = models.ForeignKey(DoctoPVLiga, related_name='liga', db_column='DOCTO_PV_LIGA_ID')
    detalle_fuente = models.ForeignKey(Docto_pv_det, related_name='fuente', db_column='DOCTO_PV_DET_FTE_ID')
    detalle_destino = models.ForeignKey(Docto_pv_det, related_name='destino', db_column='DOCTO_PV_DET_DEST_ID')

    def __unicode__(self):
        return u'%s'% (self.documento_liga, self.detalle_fuente )
        
    class Meta:
        db_table = u'doctos_pv_ligas_det'
        unique_together = (('documento_liga', 'detalle_fuente','detalle_destino',),)

class Docto_pv_det_tran_elect(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_PV_DET_ID')
    params_text         = models.TextField(db_column='PARAMS_TEXT')
    clave_servicio      = models.CharField(max_length=10, db_column='CLAVE_SERVICIO')
    caja                = models.ForeignKey(Caja, db_column='CAJA_ID')
    cajero              = models.ForeignKey(Cajero, db_column='CAJERO_ID')
    fecha               = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA')
    clave_receptor      = models.CharField(max_length=20, db_column='CLAVE_RECEPTOR')
    importe             = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    costo               = models.DecimalField(max_digits=15, decimal_places=2, db_column='COSTO')
    autorizacion        = models.CharField(max_length=20, db_column='AUTORIZACION')
    fechahora_creacion  = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')

    def __unicode__(self):
        return u'%s'% self.id 
        
    class Meta:
        db_table = u'doctos_pv_det_tran_elect'
#Cobros de documentos




#Cobros de documentos
class Forma_cobro(models.Model):
    id          = models.AutoField(primary_key=True, db_column='FORMA_COBRO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    tipo        = models.CharField(max_length=1, default='E', db_column='TIPO')

    def __unicode__(self):
        return self.nombre
        
    class Meta:
        db_table = u'formas_cobro'

class Forma_cobro_refer(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='FORMA_COBRO_REFER_ID')
    forma_cobro         = models.ForeignKey(Forma_cobro, db_column='FORMA_COBRO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return self.nombre
    class Meta:
        db_table = u'formas_cobro_refer'

class Docto_pv_cobro(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_PV_COBRO_ID')
    documento_pv        = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    tipo                = models.CharField(max_length=1, db_column='TIPO')
    forma_cobro         = models.ForeignKey(Forma_cobro, db_column='FORMA_COBRO_ID')
    importe             = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    importe_mon_doc     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_MON_DOC')
    
    def __unicode__(self):
        return u'%s'% self.id 
        
    class Meta:
        db_table = u'doctos_pv_cobros'

class Docto_pv_cobro_refer(models.Model):
    cobro_pv            = models.ForeignKey(Docto_pv_cobro, db_column='DOCTO_PV_COBRO_ID')
    forma_cobro_refer         = models.ForeignKey(Forma_cobro_refer, db_column='FORMA_COBRO_REFER_ID')
    referencia             = models.CharField(max_length=30, db_column='REFERENCIA')

    def __unicode__(self):
        return u'%s'% self.id 
        
    class Meta:
        db_table = u'doctos_pv_cobros_refer'


class ImpuestoDoctoPVManager(models.Manager):
    def get_by_natural_key(self, documento_pv,  impuesto):
        return self.get(documento_pv=documento_pv, impuesto=impuesto,)

#Impuestos de documentos
class Impuestos_docto_pv(models.Model):
    objects = ImpuestoDoctoPVManager()

    documento_pv        = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    impuesto            = models.ForeignKey(Impuesto, db_column='IMPUESTO_ID')
    venta_neta          = models.DecimalField(max_digits=15, decimal_places=2, db_column='VENTA_NETA')
    otros_impuestos     = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos= models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')
    importe_impuesto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_pv'
        unique_together = (('documento_pv', 'impuesto',),)
        

class Impuestos_grav_docto_pv(models.Model):
    documento_pv        = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    articulo            = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto            = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID', related_name='impuesto')
    impuesto_grav       = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_GARV_ID', related_name='impuesto_grav')
    impuesto_gravado    = models.DecimalField(max_digits=18, decimal_places=6, db_column='IMPUESTO_GRAVADO')
    listo               = models.CharField(max_length=1, default='N', db_column='LISTO')
    
    class Meta:
        db_table = u'impuestos_grav_doctos_pv'


################################################################
####                                                        ####
####                    MODELOS VENTAS                      ####
####                                                        ####
################################################################

class DoctoVe(models.Model):
    id              = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    folio           = models.CharField(max_length=9, db_column='FOLIO')
    fecha           = models.DateField(db_column='FECHA')
    almacen         = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    contabilizado   = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')
    cliente         = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    tipo            = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    importe_neto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')
    moneda          = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    tipo_cambio     = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estado          = models.CharField(max_length=1, db_column='ESTATUS')
    condicion_pago  = models.ForeignKey(CondicionPago, db_column='COND_PAGO_ID')
    
    #almacen = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    #condicion_pago = models.ForeignKey(CondicionesPago, on_delete= models.SET_NULL, blank=True, null=True, db_column='COND_PAGO_ID')
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'doctos_ve'

class DoctoVeDet(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_VE_DET_ID')
    docto_ve            = models.ForeignKey(DoctoVe, on_delete= models.SET_NULL, blank=True, null=True, db_column='DOCTO_VE_ID')
    articulo            = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades            = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    precio_unitario     = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    porcentaje_decuento = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto   = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')

    class Meta:
        db_table = u'doctos_ve_det'

class DoctoVeLigas(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_VE_LIGA_ID')
    factura     = models.ForeignKey(DoctoVe, db_column='DOCTO_VE_FTE_ID', related_name='factura')
    devolucion  = models.ForeignKey(DoctoVe, db_column='DOCTO_VE_DEST_ID', related_name='devolucion')

    class Meta:
        db_table = u'doctos_ve_ligas'
        
class LibresFacturasV(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'libres_fac_ve'

class LibresDevFacV(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    segmento_1    = models.CharField(max_length=99, db_column='SEGMENTO_1')
    segmento_2    = models.CharField(max_length=99, db_column='SEGMENTO_2')
    segmento_3    = models.CharField(max_length=99, db_column='SEGMENTO_3')
    segmento_4    = models.CharField(max_length=99, db_column='SEGMENTO_4')
    segmento_5    = models.CharField(max_length=99, db_column='SEGMENTO_5')
    
    def __unicode__(self):
        return u'%s' % self.id
    class Meta:
        db_table = u'libres_devfac_ve'

class ArticuloCompatibleArticulo(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articulo_id_ca", blank=True, null=True)
    articulo_compatible = models.ForeignKey(Articulos, related_name="articulo_compatible_id_ca", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.articulo_compatible

    class Meta:
        db_table = u'sic_articulocomp_art'

class ArticuloCompatibleCarpeta(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articulo_id_cc", blank=True, null=True)
    carpeta_compatible = models.ForeignKey(Carpeta, related_name="carpeta_compatible_id_cc", blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.carpeta_compatible

    class Meta:
        db_table = u'sic_articulocomp_carp'