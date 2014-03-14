from django.db import models
from datetime import datetime 
from microsip_web.libs.api.models import TipoPoliza, CondicionPago, ContabilidadCuentaContable, VentasDocumento, VentasDocumentoDetalle
from .herramientas.generar_polizas.models import *
# class CompatibilidadesArticulos(models.Model):
#     articulo = models.ForeignKey(Articulo, related_name="articulo")
#     articulos_compatibles = models.ManyToManyField(Articulos, blank=True, null=True, related_name="articulos_compatibles")
    
#     YEAR_CHOICES = []
#     for r in range(1980, (datetime.now().year+1)):
#         YEAR_CHOICES.append((r,r))

#     ano_ini = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.now().year)
#     ano_fin = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.now().year)