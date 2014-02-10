from django.db import models
from datetime import datetime 
from microsip_web.libs.api.models import *

#############################################################################################################################################################
##################################################MODELOS DE APLICACION DJANGO###############################################################################
#############################################################################################################################################################
        
class InformacionContable_CP(models.Model):
    condicion_pago_contado  = models.ForeignKey(CondicionPagoCp, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_cp_informacioncontable'

class PlantillaPolizas_CP(models.Model):
    nombre  = models.CharField(max_length=200)
    tipo    = models.ForeignKey(ConceptoCp)
    
    def __unicode__(self):
        return u'%s'%self.nombre

    class Meta:
        db_table = u'sic_cp_plantillapoliza'

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
    plantilla_poliza_CP     = models.ForeignKey(PlantillaPolizas_CP)
    cuenta_co               = models.ForeignKey(CuentaCo)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=2, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id
        
    class Meta:
        db_table = u'sic_cp_plantillapoliza_det'
