#encoding:utf-8
from django.db import models
from inventarios.models import *

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