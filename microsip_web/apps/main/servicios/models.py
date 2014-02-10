#encoding:utf-8
from django.db import models
from datetime import datetime

from microsip_web.libs.api.models import Articulos, Carpeta, Cliente

class ObjetoCliente(models.Model):
    clave  = models.CharField(max_length=20)
    cliente = models.ForeignKey(Cliente)
    descripcion  = models.CharField(max_length=150)

    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
        db_table = u'sic_ser_objetocliente'


class ServicioObjetoCliente(models.Model):
    cliente = models.ForeignKey(Cliente)
    servicio = models.ForeignKey(Articulos)
    objeto_cliente = models.ForeignKey(ObjetoCliente)
    fechahora_servicio = models.DateTimeField( auto_now_add=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    # dias_vigencia = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id
        
    class Meta:
        db_table = u'sic_ser_servobjetocliente'

        