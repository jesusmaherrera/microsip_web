from django.db import models
from django.db.models.signals import pre_save
from django.core import urlresolvers
from inventarios.models import CuentaCo

class InformacionContable_C(models.Model):
    cuenta_proveedores  = models.ForeignKey(CuentaCo)
    
    def __unicode__(self):
        return u'%s'% self.id

class Cuenta_DIOT(models.Model):
    cuenta 			= models.ForeignKey(CuentaCo)
    TIPOS_PROVEEDOR = (('04', 'Nacional'),('E', 'Extranjero'),('15', 'Global'),)
    tipo_proveedor	= models.CharField(max_length=2, choices=TIPOS_PROVEEDOR, default='04')
    TIPOS_OPERACION = (('03', 'Prestacion de Servicios Profesionales'),('06', 'Arrendamiento de Inmuebles'),('85', 'Otros'),)
    tipo_operacion	= models.CharField(max_length=2, choices=TIPOS_OPERACION, default='04')
    rfc 			= models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s'% self.cuenta