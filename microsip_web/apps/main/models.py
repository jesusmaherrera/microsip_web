#encoding:utf-8
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
 
from django.contrib.sessions.models import Session
 
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

class Registry(models.Model):
    id = models.AutoField(primary_key=True, db_column='ELEMENTO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    padre = models.ForeignKey('self', related_name='padre_a')
    valor = models.CharField(max_length=100, db_column='VALOR')

    def __unicode__(self):
        return u'%s' % self.nombre
    
    class Meta:
        db_table = u'registry'

class Moneda(models.Model):
    id = models.AutoField(primary_key=True, db_column='MONEDA_ID')
    es_moneda_local = models.CharField(default='N', max_length=1, db_column='ES_MONEDA_LOCAL')
    nombre = models.CharField(max_length=30, db_column='NOMBRE')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'monedas'

class Pais(models.Model):
    id = models.AutoField(primary_key=True, db_column='PAIS_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'paises'

class Estado(models.Model):
    id = models.AutoField(primary_key=True, db_column='ESTADO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    pais        = models.ForeignKey(Pais, db_column='PAIS_ID')

    def __unicode__(self):
        return u'%s, %s' % (self.nombre, self.pais)

    class Meta:
        db_table = u'estados'

class ActivosFijos(models.Model):
    class Meta:
        db_table = u'activos_fijos'

class AcumCuentasCoTemp(models.Model):
    class Meta:
        db_table = u'acum_cuentas_co_temp'

class Aduanas(models.Model):
    class Meta:
        db_table = u'aduanas'

class Agentes(models.Model):
    AGENTE_ID = models.AutoField(primary_key=True)

    class Meta:
        db_table = u'agentes'

class Almacenes(models.Model):
    ALMACEN_ID  = models.AutoField(primary_key=True)
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    
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

class Articulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ARTICULO_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    es_almacenable = models.CharField(default='S', max_length=1, db_column='ES_ALMACENABLE')
    seguimiento = models.CharField(default='N', max_length=1, db_column='SEGUIMIENTO')
    cuenta_ventas = models.CharField(max_length=30, blank=True, null=True, db_column='CUENTA_VENTAS')
    linea = models.ForeignKey(LineaArticulos, db_column='LINEA_ARTICULO_ID')
    nota_ventas = models.TextField(db_column='NOTAS_VENTAS', blank=True, null=True)
    unidad_venta = models.CharField(default = 'PIEZA', max_length=20, blank=True, null=True, db_column='UNIDAD_VENTA')
    unidad_compra = models.CharField(default = 'PIEZA' , max_length=20, blank=True, null=True, db_column='UNIDAD_COMPRA')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')

    puntos = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')
    hereda_puntos = models.BooleanField( db_column='SIC_HEREDA_PUNTOS')
    carpeta = models.ForeignKey(Carpeta, blank=True, null=True,db_column='SIC_CARPETA_ID')

    def __unicode__(self):
        return u'%s (%s)' % (self.nombre, self.unidad_venta)

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

class Ciudad(models.Model):
    id          = models.AutoField(primary_key=True, db_column='CIUDAD_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    estado      = models.ForeignKey(Estado, db_column='ESTADO_ID')

    def __unicode__(self):
        return u'%s, %s'%(self.nombre, self.estado)

    class Meta:
        db_table = u'ciudades'

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
    CONCEPTO_IN_ID = models.AutoField(primary_key=True)
    nombre_abrev = models.CharField(max_length=30, db_column='NOMBRE_ABREV')

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

class ConsignatariosCm(models.Model):
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

class DoctosCm(models.Model):
    class Meta:
        db_table = u'doctos_cm'

class DoctosCmDet(models.Model):
    class Meta:
        db_table = u'doctos_cm_det'

class DoctosCmLigas(models.Model):
    class Meta:
        db_table = u'doctos_cm_ligas'

class DoctosCmLigasDet(models.Model):
    class Meta:
        db_table = u'doctos_cm_ligas_det'

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
    sistema_origen      = models.CharField(default='PV', max_length=2, db_column='SISTEMA_ORIGEN')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    
    class Meta:
        db_table = u'doctos_in'

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
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='SIC_FECHAHORA_U')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='SIC_USUARIO_ULT_MODIF')
    detalle_modificaciones = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLE_MODIFICACIONES')
    detalle_modificacionestime = models.CharField(blank=True, null=True, max_length=400, db_column='SIC_DETALLETIME_MODIFICACIONES')
    unidades_syn = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='SIC_UNIDADES_SYN')
    
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
    costo_unitario  = models.DecimalField(default=0, max_digits=18, decimal_places=2, db_column='COSTO_UNITARIO')
    costo_total     = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='COSTO_TOTAL')
    metodo_costeo   = models.CharField(default='C', max_length=1, db_column='METODO_COSTEO')
    cancelado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado        = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='APLICADO')
    costeo_pend     = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='COSTEO_PEND')
    pedimento_pend  = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='PEDIMENTO_PEND')
    rol             = models.CharField(default='N', max_length=1, db_column='ROL')
    fecha           = models.DateField(auto_now=True, blank=True, null=True, db_column='FECHA') 
    
    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'doctos_in_det'

class DesgloseEnDiscretos(models.Model):
    id = models.AutoField(primary_key=True, db_column='DESGLOSE_EN_DISCRETOS')
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
    sic_nuevo = models.CharField(default='N', max_length=1, db_column='SIC_NUEVO')
    
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
    estatus = models.CharField( default = 'A', max_length = 1, db_column = 'ESTATUS' )
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
    id                  = models.AutoField(primary_key=True, db_column='DIR_CLI_ID')
    cliente             = models.ForeignKey(Cliente, db_column='CLIENTE_ID')

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

class TiposImpuestos(models.Model):
    id      = models.AutoField(primary_key=True, db_column='TIPO_IMPTO_ID')
    nombre  = models.CharField(max_length=30, db_column='NOMBRE')
    tipo    = models.CharField(max_length=30, db_column='TIPO')

    class Meta:
        db_table = u'tipos_impuestos'

class Impuesto(models.Model):
    id              = models.AutoField(primary_key=True, db_column='IMPUESTO_ID')
    tipoImpuesto    = models.ForeignKey(TiposImpuestos, on_delete= models.SET_NULL, blank=True, null=True, db_column='TIPO_IMPTO_ID')
    nombre          = models.CharField(max_length=30, db_column='NOMBRE')
    porcentaje      = models.DecimalField(default=0, blank=True, null=True, max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')

    def __unicode__(self):
        return self.nombre
        
    class Meta:
        db_table = u'impuestos'

class ImpuestosArticulo(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPUESTO_ART_ID')
    articulo    = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto    = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')

    def __unicode__(self):
        return self.impuesto

    class Meta:
        db_table = u'impuestos_articulos'

################################################################
####                                                        ####
####               MODELOS CUENTAS POR PAGAR                ####
####                                                        ####
################################################################

class CondicionPagoCp(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'condiciones_pago_cp'

class ClavesProveedores(models.Model):    
    class Meta:
        db_table = u'claves_proveedores'

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
    cliente           	= models.ForeignKey(Cliente, db_column='CLIENTE_ID')
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
    estado                  = models.CharField(max_length=1, db_column='ESTATUS')
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
    refer_reting            = models.CharField(max_length=50, db_column='REFER_RETING')
    unidad_comprom          = models.CharField(default='N', max_length=1, db_column='UNID_COMPROM')    
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    
    impuesto_sustituido     = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID', related_name='impuesto_sustituido')
    impuesto_sustituto      = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID', related_name='impuesto_sustituto')
    
    es_cfd                  = models.CharField(default='N', max_length=1, db_column='ES_CFD')
    modalidad_facturacion   = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    enviado                 = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    email_envio             = models.EmailField(db_column='EMAIL_ENVIO')
    fecha_envio             = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ENVIO')

    usuario_creador         = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
    
    puntos                  = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico      = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')
    def __unicode__(self):
        return u'%s'% self.id 
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
    vendedor                = models.ForeignKey(Vendedor, db_column='VENDEDOR_ID')
    porcentaje_comis        = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_COMIS')
    rol                     = models.CharField(max_length=1, db_column='ROL')
    notas                   = models.TextField(db_column='NOTAS')
    es_tran_elect           = models.CharField(default='N', max_length=1, db_column='ES_TRAN_ELECT')
    estatus_tran_elect      = models.CharField(max_length=1, db_column='ESTATUS_TRAN_ELECT')
    posicion                =  models.IntegerField(db_column='POSICION')
    puntos                  = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico      = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')

    def __unicode__(self):
        return u'%s'% self.id 
        
    class Meta:
        db_table = u'doctos_pv_det'

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

#Impuestos de documentos
class Impuestos_docto_pv(models.Model):
    documento_pv        = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    impuesto            = models.ForeignKey(Impuesto, db_column='IMPUESTO_ID')
    venta_neta          = models.DecimalField(max_digits=15, decimal_places=2, db_column='VENTA_NETA')
    otros_impuestos     = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos= models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTOS')
    importe_impuesto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_pv'
        

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