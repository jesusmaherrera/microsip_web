#encoding:utf-8
from microsip_web.libs.api.models import Cliente, Articulo, VentasDocumento
from django.db import models

class ClienteArticulo(models.Model):
    cliente = models.ForeignKey(Cliente)
    descripccion  = models.CharField(max_length=150)
    clave = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_cliente_articulo'

class ClienteArticuloServicio(models.Model):
    servicio = models.ForeignKey(Articulo)
    cliente_articulo = models.ForeignKey(ClienteArticulo)
    fecha = models.DateTimeField(auto_now=True)
    precio_servicio = models.DecimalField( default = 0, blank = True, null = True, max_digits = 15, decimal_places = 2)
    documento =  models.ForeignKey(VentasDocumento)
    alerta_fecha = models.DateTimeField()

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_cliente_articulo_servicio'