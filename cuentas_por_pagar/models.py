from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers
from inventarios.models import *

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

class CondicionPagoCp(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'condiciones_pago_cp'

class DoctosCp(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_CP_ID')
    concepto            = models.ForeignKey(ConceptoCp, db_column='CONCEPTO_CP_ID')
    folio               = models.CharField(max_length=9, db_column='FOLIO')
    naturaleza_concepto = models.CharField(max_length=1, db_column='NATURALEZA_CONCEPTO')
    fecha               = models.DateField(auto_now=True, db_column='FECHA') 
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
    importe_neto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPUESTO')
    iva_retenido    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IVA_RETENIDO')
    
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

#############################################################################################################################################################
##################################################MODELOS DE APLICACION DJANGO###############################################################################
#############################################################################################################################################################
class InformacionContable_CP(models.Model):
    condicion_pago_contado  = models.ForeignKey(CondicionPagoCp, blank=True, null=True)
    depto_general_cont      = models.ForeignKey(DeptoCo)
    
    def __unicode__(self):
        return u'%s'% self.id

class PlantillaPolizas_CP(models.Model):
    nombre  = models.CharField(max_length=200)
    tipo    = models.ForeignKey(ConceptoCp)
    
    def __unicode__(self):
        return u'%s'%self.nombre

class DetallePlantillaPolizas_CP(models.Model):
    TIPOS = (('C', 'Cargo'),('A', 'Abono'),)
    VALOR_TIPOS =(
        ('Compras', 'Compras'),
        ('Proveedores', 'Proveedores'),
        ('Bancos', 'Bancos'),
        ('Descuentos', 'Descuentos'),
        ('Anticipos','Anticipos'),
        ('IVA', 'IVA'),
        ('IVA Retenido', 'IVA Retenido'),
        ('Segmento_1', 'Segmento 1'),
        ('Segmento_2', 'Segmento 2'),
        ('Segmento_3', 'Segmento 3'),
        ('Segmento_4', 'Segmento 4'),
        ('Segmento_5', 'Segmento 5'),
    )
    VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)

    posicion                = models.CharField(max_length=2)
    plantilla_poliza_CP     = models.ForeignKey(PlantillaPolizas_CP)
    cuenta_co               = models.ForeignKey(CuentaCo)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=2, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id
