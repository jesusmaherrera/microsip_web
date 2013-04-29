#encoding:utf-8
from django.db import models
from inventarios.models import *

class Cajero(models.Model):
    id          = models.AutoField(primary_key=True, db_column='CAJERO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')

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
    fecha                   = models.DateField(auto_now=True,db_column='FECHA')
    hora                    = models.TimeField(auto_now=True, db_column='HORA')
    cajero                  = models.ForeignKey(Cajero, db_column='CAJERO_ID')
    clave_cliente           = models.CharField(max_length=20, db_column='CLAVE_CLIENTE')
    cliente                 = models.ForeignKey(Cliente, db_column='CLIENTE_ID')
    clave_cliente_fac       = models.CharField(max_length=20, db_column='CLAVE_CLIENTE_FAC')
    cliente_fac             = models.ForeignKey(Cliente, db_column='CLIENTE_FAC_ID')
    direccion_cliente       = models.ForeignKey(DirCliente, db_column='DIR_CLI_ID')
    almacen                 = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')
    moneda                  = models.ForeignKey(Moneda, db_column='MONEDA_ID')
    impuesto_incluido       = models.CharField(default='S', max_length=1, db_column='IMPUESTO_INCLUIDO')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    tipo_descuento          = models.CharField(max_length=1, db_column='TIPO_DSCTO')
    porcentaje_descuento    = models.DecimalField(max_digits=9, decimal_places=6, db_column='DSCTO_PCTJE')
    importe_descuento       = models.DecimalField(max_digits=15, decimal_places=2, db_column='DSCTO_IMPORTE')
    estado                  = models.CharField(max_length=1, db_column='ESTATUS')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    importe_neto            = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos         = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')

    importe_donativo        = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_DONATIVO')
    total_fpgc              = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_FPGC')
        
    ticket_emitido          = models.CharField(default='N', db_column='TICKET_EMITIDO')
    forma_emitido           = models.CharField(default='N', db_column='FORMA_EMITIDA')
    forma_global_emitida    = models.CharField(default='N', db_column='FORMA__GLOBAL_EMITIDA')
    contabilizado           = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')

    sistema_origen          = models.CharField(default='PV', max_length=2, db_column='SISTEMA_ORIGEN')
    vendedor                = models.ForeignKey(Vendedor, db_column='VENDEDOR_ID')
    cargar_sun              = models.CharField(default='S', max_length=1, db_column='CARGAR_SUN')
    persona                 = models.CharField(max_length=50, db_column='PERSONA')
    refer_reting            = models.CharField(max_length=50, db_column='REFER_RETING')
    unidad_comprom          = models.CharField(default='N', max_length=1, db_column='UNID_COMPROM')    
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    
    impuesto_sustituido     = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID')
    impuesto_sustituto      = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID')
    
    es_cfd                  = models.CharField(default='N', max_length=1, db_column='ES_CFD')
    modalidad_facturacion   = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    enviado                 = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    email_envio             = models.EmailField(db_column='EMAIL_ENVIO')
    fecha_envio             = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ENVIO')

    usuario_creador         = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
    
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
    porcentaje_decuento     = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto       = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')
    precio_modificado       = models.CharField(default='N', max_length=1, db_column='PRECIO_MODIFICADO')
    vendedor                = models.ForeignKey(Vendedor, db_column='VENDEDOR_ID')
    porcentaje_comis        = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_COMIS')
    rol                     = models.CharField(max_length=1, db_column='ROL')
    notas                   = models.TextField(db_column='NOTAS')
    es_tran_elect           = models.CharField(default='N', max_length=1, db_column='ES_TRAN_ELECT')
    estatus_tran_elect      = models.CharField(max_length=1, db_column='ESTATUS_TRAN_ELECT')
    posicion                =  models.IntegerField(db_column='POSICION')

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
    id                      = models.AutoField(primary_key=True, db_column='FORMA_COBRO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return self.nombre
        
    class Meta:
        db_table = u'doctos_pv_cobros'

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
    impuesto            = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')
    venta_neta          = models.DecimalField(max_digits=15, decimal_places=2, db_column='VENTA_NETA')
    otros_impuestos     = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos= models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTOS')
    importe_impuesto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_pv'

class Impuestos_grav_docto_pv(models.Model):
    documento_pv        = models.ForeignKey(Docto_PV, db_column='DOCTO_PV_ID')
    articulo            = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto            = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')
    impuesto_grav       = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')
    impuesto_gravado    = models.DecimalField(max_digits=18, decimal_places=6, db_column='IMPUESTO_GRAVADO')
    listo               = models.CharField(max_length=1, default='N', db_column='LISTO')
    
    class Meta:
        db_table = u'impuestos_grav_doctos_pv'

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class InformacionContable_pv(models.Model):
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

class PlantillaPolizas_pv(models.Model):
    nombre  = models.CharField(max_length=200)
    TIPOS =(
        ('V', 'Ventas de mostrador'),
        ('D', 'Devoluciones'),
        ('', 'Cobros ctas. por cobrar'),
    )
    tipo    = models.CharField(max_length=2, choices=TIPOS, default='V')
    
    def __unicode__(self):
        return u'%s'%self.nombre

class DetallePlantillaPolizas_pv(models.Model):
    TIPOS = (('C', 'Cargo'),('A', 'Abono'),)
    VALOR_TIPOS =(
        ('Ventas', 'Ventas'),
        ('Clientes', 'Clientes'),
        ('Bancos', 'Bancos'),
        ('Descuentos', 'Descuentos'),
        ('IVA', 'IVA'),
        ('Segmento_1', 'Segmento 1'),
        ('Segmento_2', 'Segmento 2'),
        ('Segmento_3', 'Segmento 3'),
        ('Segmento_4', 'Segmento 4'),
        ('Segmento_5', 'Segmento 5'),
    )
    VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
    
    posicion                = models.CharField(max_length=2)
    plantilla_poliza_pv     = models.ForeignKey(PlantillaPolizas_pv)
    cuenta_co               = models.ForeignKey(CuentaCo)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=2, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id