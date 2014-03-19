#encoding:utf-8
from django.db import models
from microsip_web.libs.api.models import CuentasXCobrarConcepto, ContabilidadCuentaContable, ContabilidadDepartamento, CuentasXCobrarDocumento, CondicionPago, CuentasXCobrarDocumentoCreditoLibres, CuentasXCobrarDocumentoImportes, CuentasXCobrarDocumento

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class InformacionContable_CC(models.Model):
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id
    
    class Meta:
        db_table = u'sic_cc_informacioncontable'

class PlantillaPolizas_CC(models.Model):
    nombre  = models.CharField(max_length=200)
    tipo    = models.ForeignKey(CuentasXCobrarConcepto)
    
    def __unicode__(self):
        return u'%s'%self.nombre

    class Meta:
        db_table = u'sic_cc_plantillapoliza'

class DetallePlantillaPolizas_CC(models.Model):
    TIPOS = (('C', 'Cargo'),('A', 'Abono'),)
    VALOR_TIPOS =(
        ('Ventas', 'Ventas'),
        ('Clientes', 'Clientes'),
        ('Bancos', 'Bancos'),
        ('Descuentos', 'Descuentos'),
        ('IVA', 'IVA'),
        ('IVA Retenido', 'IVA Retenido'),
        ('ISR Retenido', 'ISR Retenido'),
        ('Segmento_1', 'Segmento 1'),
        ('Segmento_2', 'Segmento 2'),
        ('Segmento_3', 'Segmento 3'),
        ('Segmento_4', 'Segmento 4'),
        ('Segmento_5', 'Segmento 5'),
    )
    VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
    
    posicion                = models.CharField(max_length=2)
    plantilla_poliza_CC     = models.ForeignKey(PlantillaPolizas_CC)
    cuenta_co               = models.ForeignKey(ContabilidadCuentaContable)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=2, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id

    class Meta:
        db_table = u'sic_cc_plantillapoliza_det'

