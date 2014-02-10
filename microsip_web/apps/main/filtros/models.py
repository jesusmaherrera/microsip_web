#encoding:utf-8
from django.db import models
from datetime import datetime

from microsip_web.libs.api.models import Articulos, Carpeta


        
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