from django.db import models
from datetime import datetime 

from microsip_web.libs.api.models import TipoPoliza, CondicionPago, ContabilidadCuentaContable, VentasDocumento, VentasDocumentoDetalle, ContabilidadDepartamento, VentasDocumentoFacturaLibres, VentasDocumentoImpuesto, Impuesto
################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class clientes_config_cuenta(models.Model):
    CAMPOS_CLIENTE = (('cuenta_1', 'cuenta_1'),('cuenta_2', 'cuenta_2'),('cuenta_3', 'cuenta_3'),('cuenta_4', 'cuenta_4'),('cuenta_5', 'cuenta_5'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
    VALOR_IVA_TIPOS             = (('A', 'TODOS'),('I', 'Solo IVA'),('0', 'Solo 0%'),)

    campo_cliente           = models.CharField(max_length=20, unique=True, choices=CAMPOS_CLIENTE)
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')

    class Meta:
        db_table = u'sic_ve_clientconfigcuenta'

class InformacionContable_V(models.Model):
    tipo_poliza_ve          = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_ve')
    tipo_poliza_dev         = models.ForeignKey(TipoPoliza, blank=True, null=True, related_name='tipo_poliza_dev')
    condicion_pago_contado  = models.ForeignKey(CondicionPago, blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_ve_informacioncontable'

class PlantillaPolizas_V(models.Model):
    nombre  = models.CharField(max_length=200)
    TIPOS   = (('F', 'Facturas'),('D', 'Devoluciones'),)
    tipo    = models.CharField(max_length=2, choices=TIPOS, default='F')

    def __unicode__(self):
        return u'%s'%self.nombre
    
    class Meta:
        db_table = u'sic_ve_plantillapoliza'

class DetallePlantillaPolizas_V(models.Model):
    TIPOS = (('C', 'Cargo'),('A', 'Abono'),)
    VALOR_TIPOS =(
        ('Ventas', 'Ventas'),
        ('Clientes', 'Clientes'),
        ('Bancos', 'Bancos'),
        # ('Descuentos', 'Descuentos'),
        ('IVA', 'IVA'),
        ('IEPS', 'IEPS'),
        ('Segmento_1', 'Segmento 1'),
        ('Segmento_2', 'Segmento 2'),
        ('Segmento_3', 'Segmento 3'),
        ('Segmento_4', 'Segmento 4'),
        ('Segmento_5', 'Segmento 5'),
    )
    VALOR_IVA_TIPOS             = (('A', 'Todos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
    VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)

    posicion                = models.CharField(max_length=2)
    plantilla_poliza_v      = models.ForeignKey(PlantillaPolizas_V)
    cuenta_co               = models.ForeignKey(ContabilidadCuentaContable)
    tipo                    = models.CharField(max_length=2, choices=TIPOS, default='C')
    asiento_ingora          = models.CharField(max_length=3, blank=True, null=True)
    valor_tipo              = models.CharField(max_length=20, choices=VALOR_TIPOS)
    valor_iva               = models.CharField(max_length=2, choices=VALOR_IVA_TIPOS, default='A')
    valor_contado_credito   = models.CharField(max_length=10, choices=VALOR_CONTADO_CREDITO_TIPOS, default='Ambos')

    def __unicode__(self):
        return u'%s'%self.id

    class Meta:
        db_table = u'sic_ve_plantillapoliza_det'
