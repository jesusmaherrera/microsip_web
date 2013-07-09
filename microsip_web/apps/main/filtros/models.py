#encoding:utf-8
from django.db import models
from datetime import datetime

from microsip_web.apps.main.models import Articulos

class ArticuloCompatibleArticulo(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articulo_id_ca", blank=True, null=True)
    articulo_compatible = models.ForeignKey(Articulos, related_name="articulo_compatible_id_ca", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id

class ArticuloCompatibleCarpeta(models.Model):
    articulo = models.ForeignKey(Articulos, related_name="articulo_id_cc", blank=True, null=True)
    #carpeta_compatible = models.ForeignKey(Carpeta, related_name="carpeta_compatible_id_cc", blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.id
        
# class CarpetaCompatibleArticulo(models.Model):
#     carpeta_articulos = models.ForeignKey(Carpeta, related_name="carpeta_articulos", blank=True, null=True)
#     compatible_articulo = models.ForeignKey(Articulos, related_name="compatible_articuloca", blank=True, null=True)

#     def __unicode__(self):
#         return u'%s'% self.compatible_articulo

#     class Meta:
#         db_table = u'sic_filtros_carpetaCompArticulo'



# class ClasificacionCompatibleClasificacion(models.Model):
#     clasificacion = models.ForeignKey(GruposGrupo, related_name="clasificacioncc", blank=True, null=True)
#     compatible_clasificacion = models.ForeignKey(GruposGrupo, related_name="compatible_clasificacioncc", blank=True, null=True)

#     def __unicode__(self):
#         return u'%s'% self.compatible_clasificacion