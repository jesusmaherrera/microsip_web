#encoding:utf-8
from django.db import models
from datetime import datetime 
from django.db.models.signals import pre_save
from django.core import urlresolvers
from microsip_web.apps.main.models import Articulos, SeccionArticulos

########################################################################################################


class ArticuloCompatibleArticulo(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articuloaa", blank=True, null=True)
    compatible_articulo = models.ForeignKey(Articulos, related_name="compatible_articuloaa", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.compatible_articulo

class ClasificacionCompatibleArticulo(models.Model):
    clasificacion = models.ForeignKey(SeccionArticulos, related_name="clasificacionca", blank=True, null=True)
    compatible_articulo = models.ForeignKey(Articulos, related_name="compatible_articuloca", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.compatible_articulo

class ArticuloCompatibleClasificacion(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articuloac", blank=True, null=True)
    compatible_clasificacion = models.ForeignKey(SeccionArticulos, related_name="compatible_clasificacionac", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.compatible_clasificacion

class ClasificacionCompatibleClasificacion(models.Model):
    clasificacion = models.ForeignKey(SeccionArticulos, related_name="clasificacioncc", blank=True, null=True)
    compatible_clasificacion = models.ForeignKey(SeccionArticulos, related_name="compatible_clasificacioncc", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.compatible_clasificacion