#encoding:utf-8
from django.db import models
import datetime

from microsip_web.libs.api.models import (CondicionPago, Impuesto, ContabilidadCuentaContable, Almacen, Articulo, ClienteTipo, TipoPoliza, PuntoVentaDocumento,
    PuntoVentaDocumentoDetalle, PuntoVentaCobro,  PuntoVentaDocumentoLiga)

################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class InformacionContable_pv(models.Model):
    # tipo_poliza_ve_m          = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_ve_m')
    # tipo_poliza_dev_m         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_dev_m')
    # tipo_poliza_cc         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_cc')    

    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_pv_informacioncontable'

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

    class Meta:
        db_table = u'sic_pv_plantillapoliza'


class RamaDetallesPlantilla(models.Model):
    nombre = models.CharField(max_length=150)
    nivel = models.CharField(max_length=1, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'sic_pv_rama_plantpol_det'

class DetallePlantillaPolizas_pv(models.Model):
    plantilla_poliza_pv = models.ForeignKey(PlantillaPolizas_pv)
    posicion = models.CharField(max_length=2)
    rama = models.ForeignKey(RamaDetallesPlantilla, blank=True, null=True)

    TIPOS_ASIENTO = (('C', 'Cargo'),('A', 'Abono'),)
    tipo_asiento = models.CharField(max_length=2, choices=TIPOS_ASIENTO)
    
    TIPOS_VALOR =(
        ('Ventas', 'Ventas'),
        ('Clientes', 'Clientes'),
        ('Bancos', 'Bancos'),
        ('Descuentos', 'Descuentos'),
        ('IVA', 'Impuestos'),
    )
    tipo_valor = models.CharField(max_length=20, choices=TIPOS_VALOR)

    TIPOS_CONDICIONPAGO = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
    tipo_condicionpago = models.CharField(max_length=10, choices=TIPOS_CONDICIONPAGO, blank=True, null=True, default='Ambos')

    impuesto = models.ForeignKey(Impuesto, blank=True, null=True)
    cuenta_co = models.ForeignKey(ContabilidadCuentaContable)
    asiento_ingora = models.CharField(max_length=2, blank=True, null=True)

    def __unicode__(self):
        return u'%s'%self.id

    class Meta:
        db_table = u'sic_pv_plantillapoliza_det'