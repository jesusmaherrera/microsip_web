from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers
from microsip_web.apps.inventarios.models import *
from microsip_web.apps.contabilidad.models import *

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

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class clientes_config_cuenta(models.Model):
    CAMPOS_CLIENTE = (('cuenta_1', 'cuenta_1'),('cuenta_2', 'cuenta_2'),('cuenta_3', 'cuenta_3'),('cuenta_4', 'cuenta_4'),('cuenta_5', 'cuenta_5'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
    VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)

    campo_cliente           = models.CharField(max_length=20, unique=True, choices=CAMPOS_CLIENTE)
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')

class InformacionContable_V(models.Model):
    tipo_poliza_ve          = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_ve')
    tipo_poliza_dev         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_dev')
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

class PlantillaPolizas_V(models.Model):
    nombre  = models.CharField(max_length=200)
    TIPOS   = (('F', 'Facturas'),('D', 'Devoluciones'),)
    tipo    = models.CharField(max_length=2, choices=TIPOS, default='F')

    def __unicode__(self):
        return u'%s'%self.nombre

class DetallePlantillaPolizas_V(models.Model):
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
    plantilla_poliza_v      = models.ForeignKey(PlantillaPolizas_V)
    cuenta_co               = models.ForeignKey(CuentaCo)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=3, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id

# class CompatibilidadesArticulos(models.Model):
#     articulo = models.ForeignKey(Articulos, related_name="articulo")
#     articulos_compatibles = models.ManyToManyField(Articulos, blank=True, null=True, related_name="articulos_compatibles")
    
#     YEAR_CHOICES = []
#     for r in range(1980, (datetime.now().year+1)):
#         YEAR_CHOICES.append((r,r))

#     ano_ini = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.now().year)
#     ano_fin = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.now().year)