#encoding:utf-8
from django.db import models
from django.db import router

class VentasDocumentoBase(models.Model):
    id              = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    folio           = models.CharField(max_length=9, db_column='FOLIO')
    almacen = models.ForeignKey('Almacenes', db_column='ALMACEN_ID')
    cliente = models.ForeignKey('Cliente', db_column='CLIENTE_ID')
    moneda = models.ForeignKey('Moneda', db_column='MONEDA_ID')
    condicion_pago = models.ForeignKey('CondicionPago', db_column='COND_PAGO_ID')

    fecha           = models.DateField(db_column='FECHA')
    contabilizado   = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')
    descripcion         = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    tipo            = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    importe_neto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')
    tipo_cambio     = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estado          = models.CharField(max_length=1, db_column='ESTATUS')

    class Meta:
        db_table = u'doctos_ve'
        abstract = True

class VentasDocumentoDetalleBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_VE_DET_ID')
    docto_ve = models.ForeignKey('DoctoVe', on_delete= models.SET_NULL, blank=True, null=True, db_column='DOCTO_VE_ID')
    articulo = models.ForeignKey('Articulos', on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    porcentaje_decuento = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')

    class Meta:
        db_table = u'doctos_ve_det'
        abstract = True

class VentasDocumentoLigaBase(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_VE_LIGA_ID')
    factura     = models.ForeignKey('DoctoVe', db_column='DOCTO_VE_FTE_ID', related_name='factura')
    devolucion  = models.ForeignKey('DoctoVe', db_column='DOCTO_VE_DEST_ID', related_name='devolucion')

    class Meta:
        db_table = u'doctos_ve_ligas'
        abstract = True
        
class VentasDocumentoFacturaLibresBase(models.Model):
    id            = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    
    class Meta:
        db_table = u'libres_fac_ve'
        abstract = True

class VentasDocumentoFacturaDevLibresBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_VE_ID')
    
    
    class Meta:
        db_table = u'libres_devfac_ve'
        abstract = True