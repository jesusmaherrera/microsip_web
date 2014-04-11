#encoding:utf-8
from django.db import models
from datetime import datetime 
from microsip_web.libs.api.models import (Articulo, ImpuestosArticulo, ArticuloPrecio, ArticuloClave, 
	ConexionDB, LineaArticulos, InventariosConcepto, InventariosDocumento, InventariosDocumentoDetalle, Almacen, InventariosDocumentoIF, InventariosDocumentoIFDetalle, ArticuloDiscreto, )

# class DocumentoInventarioAjustes(models.Model):
#     no_inventario = models.CharField(max_length=150)
    

#     def __unicode__(self):
#         return self.nombre

#     class Meta:
#         db_table = u'sic_pv_rama_plantpol_det'



