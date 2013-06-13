#encoding:utf-8
from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers

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
    puntos              = models.IntegerField(db_column='PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='DINERO_ELECTRONICO')
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'grupos_lineas'

class LineaArticulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='LINEA_ARTICULO_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    grupo               = models.ForeignKey(GrupoLineas, db_column='GRUPO_LINEA_ID')
    puntos              = models.IntegerField(db_column='PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='DINERO_ELECTRONICO')
    hereda_puntos       = models.BooleanField( db_column='HEREDA_PUNTOS')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'lineas_articulos'

class Articulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='ARTICULO_ID')
    nombre              = models.CharField(max_length=100, db_column='NOMBRE')
    es_almacenable      = models.CharField(default='S', max_length=1, db_column='ES_ALMACENABLE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    linea               = models.ForeignKey(LineaArticulos, db_column='LINEA_ARTICULO_ID')
    puntos              = models.IntegerField(db_column='PUNTOS')
    dinero_electronico  = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='DINERO_ELECTRONICO')
    hereda_puntos       = models.BooleanField( db_column='HEREDA_PUNTOS')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'articulos'

class ArticulosClientes(models.Model):
    class Meta:
        db_table = u'articulos_clientes'

class ArticulosDiscretos(models.Model):
    class Meta:
        db_table = u'articulos_discretos'

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

class Cajas(models.Model):
    class Meta:
        db_table = u'cajas'

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
    clave       = models.CharField(max_length=1, db_column='CLAVE')

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

class DesgloseEnDiscretos(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos'

class DesgloseEnDiscretosCm(models.Model):
    class Meta:
        db_table = u'desglose_en_discretos_cm'

class DesgloseEnDiscretosInvfis(models.Model):
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
    fecha               = models.DateField(auto_now_add=True, db_column='FECHA') 
    cancelado           = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado            = models.CharField(default='N',blank=True, null=True, max_length=1, db_column='APLICADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    usuario_creador     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion  = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion= models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif   = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'doctos_invfis'

class DoctosInvfisDet(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_INVFIS_DET_ID')
    docto_invfis= models.ForeignKey(DoctosInvfis, db_column='DOCTO_INVFIS_ID')
    clave       = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo    = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    unidades    = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')
    
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
    unidades        = models.IntegerField(default=0, blank=True, null=True, db_column='UNIDADES')
    costo_unitario  = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=2, db_column='COSTO_UNITARIO')
    costo_total     = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='COSTO_TOTAL')
    metodo_costeo   = models.CharField(default='C', max_length=1, db_column='METODO_COSTEO')
    cancelado       = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CANCELADO')
    aplicado        = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='APLICADO')
    costeo_pend     = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='COSTEO_PEND')
    pedimento_pend  = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='PEDIMENTO_PEND')
    rol             = models.CharField(default='N', max_length=1, db_column='ROL')
    fecha           = models.DateField(blank=True, null=True, db_column='FECHA') 
    #centros_costo = models.ForeignKey(CentrosCosto, db_column='CENTRO_COSTO_ID', blank=True, null=True,)

    class Meta:
        db_table = u'doctos_in_det'
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

class TipoCliente(models.Model):
    id              = models.AutoField(primary_key=True, db_column='TIPO_CLIENTE_ID')
    nombre          = models.CharField(max_length=100, db_column='NOMBRE')
    valor_puntos    = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='VALOR_PUNTOS')

    def __unicode__(self):
        return self.nombre
        
    class Meta:
        db_table = u'tipos_clientes'

class Cliente(models.Model):
    id                          = models.AutoField(primary_key=True, db_column='CLIENTE_ID')
    nombre                      = models.CharField(max_length=100, db_column='NOMBRE')
    cuenta_xcobrar              = models.CharField(max_length=9, db_column='CUENTA_CXC')
    TIPOS = (('N', 'No Aplica'),('P', 'Puntos'),('D', 'Dinero Electronico'),)
    puntos                      = models.IntegerField(db_column='PUNTOS')
    dinero_electronico          = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='DINERO_ELECTRONICO')
    tipo_tarjeta                = models.CharField(default='N', max_length=1, choices=TIPOS, db_column='TIPO_TARJETA')
    tipo_cliente                = models.ForeignKey(TipoCliente, db_column='TIPO_CLIENTE_ID')
    hereda_valorpuntos          = models.BooleanField(db_column='HEREDA_VALORPUNTOS')
    valor_puntos                = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='VALOR_PUNTOS')
    hereda_puntos_a             = models.ForeignKey('self', db_column='HEREDAR_PUNTOS_A', related_name='hereda_puntos_a_cliente',blank=True, null=True)
    cuenta_1 = models.ForeignKey(CuentaCo, db_column='CUENTA_1', blank=True, null=True, related_name='cuenta_1')
    cuenta_2 = models.ForeignKey(CuentaCo, db_column='CUENTA_2', blank=True, null=True, related_name='cuenta_2')
    cuenta_3 = models.ForeignKey(CuentaCo, db_column='CUENTA_3', blank=True, null=True, related_name='cuenta_3')
    cuenta_4 = models.ForeignKey(CuentaCo, db_column='CUENTA_4', blank=True, null=True, related_name='cuenta_4')
    cuenta_5 = models.ForeignKey(CuentaCo, db_column='CUENTA_5', blank=True, null=True, related_name='cuenta_5')


    def __unicode__(self):
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

    class Meta:
        db_table = u'impuestos'

class ImpuestosArticulo(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPUESTO_ART_ID')
    articulo    = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto    = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')

    class Meta:
        db_table = u'impuestos_articulos'



