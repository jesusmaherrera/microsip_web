#encoding:utf-8
from django.db import models
from microsip_web.apps.main.models import *
from microsip_web.apps.contabilidad.models import *

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class InformacionContable_pv(models.Model):
    tipo_poliza_ve_m          = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_ve_m')
    tipo_poliza_dev_m         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_dev_m')
    tipo_poliza_cc         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_cc')    

    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

class PlantillaPolizas_pv(models.Model):
    nombre  = models.CharField(max_length=200)
    TIPOS =(
        ('V', 'Ventas de mostrador'),
        ('D', 'Devoluciones'),
        ('P', 'Cobros ctas. por cobrar'),
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
