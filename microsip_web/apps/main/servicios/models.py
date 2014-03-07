#encoding:utf-8
from django.db import models
from datetime import datetime

from microsip_web.libs.api.models import Articulo, Carpeta, Cliente

class ArticuloCliente(models.Model):
    clave  = models.CharField(max_length=20)
    cliente = models.ForeignKey(Cliente)
    descripcion  = models.CharField(max_length=150)

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_articulo_cliente'


class ArticuloClienteMantenimiento(models.Model):
    articulo = models.ForeignKey(Articulo)
    articulo_cliente = models.ForeignKey(ArticuloCliente)
    fechahora = models.DateTimeField( auto_now_add=True)
    factura = models.ForeignKey(DocumentoVentas)

    alerta_fechahora = models.DateTimeField( auto_now_add=True)
    
    def __unicode__(self):
        return u'%s'% self.id
        
    class Meta:
        db_table = u'sic_ser_servobjetocliente'

        