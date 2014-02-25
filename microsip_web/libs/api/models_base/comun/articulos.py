#encoding:utf-8
from django.db import models

class GrupoLineaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='GRUPO_LINEA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas= models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    
    class Meta:
        db_table = u'grupos_lineas'
        abstract  = True

class LineaArticulosBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='LINEA_ARTICULO_ID')
    grupo = models.ForeignKey('GrupoLineas', db_column='GRUPO_LINEA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas = models.CharField(max_length=30, db_column='CUENTA_VENTAS')

    class Meta:
        db_table = u'lineas_articulos'
        abstract  = True

class ArticuloBase(models.Model):
    id = models.AutoField( primary_key = True, db_column = 'ARTICULO_ID' )
    linea = models.ForeignKey('LineaArticulos', db_column = 'LINEA_ARTICULO_ID' )
    nombre = models.CharField( max_length = 100, db_column = 'NOMBRE' )
    es_almacenable = models.CharField( default = 'S', max_length = 1, db_column = 'ES_ALMACENABLE' )
    estatus = models.CharField( default = 'A', max_length = 1, db_column = 'ESTATUS' )
    seguimiento = models.CharField( default = 'N', max_length = 1, db_column = 'SEGUIMIENTO' )
    cuenta_ventas = models.CharField( max_length = 30, blank = True, null = True, db_column = 'CUENTA_VENTAS' )
    nota_ventas = models.TextField( db_column = 'NOTAS_VENTAS', blank = True, null = True )
    unidad_venta = models.CharField( default = 'PIEZA', max_length = 20, blank = True, null = True, db_column = 'UNIDAD_VENTA' )
    unidad_compra = models.CharField( default = 'PIEZA' , max_length = 20, blank = True, null = True, db_column = 'UNIDAD_COMPRA' )
    costo_ultima_compra = models.DecimalField( default = 0, blank = True, null = True, max_digits = 18, decimal_places = 6, db_column = 'COSTO_ULTIMA_COMPRA' )

    usuario_ult_modif = models.CharField( blank = True, null = True, max_length = 31, db_column = 'USUARIO_ULT_MODIF' )
    fechahora_ult_modif = models.DateTimeField( auto_now = True, blank = True, null = True, db_column = 'FECHA_HORA_ULT_MODIF' )

    class Meta:
        db_table = u'articulos'
        abstract  = True

class ArticuloClaveRolBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='ROL_CLAVE_ART_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    class Meta:
        db_table = u'roles_claves_articulos'
        abstract  = True

class ArticuloClaveBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLAVE_ARTICULO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE_ARTICULO')
    articulo = models.ForeignKey('Articulos', db_column='ARTICULO_ID')
    rol = models.ForeignKey('RolesClavesArticulos', db_column='ROL_CLAVE_ART_ID')
    
    class Meta:
        db_table = u'claves_articulos'
        abstract  = True

class ArticuloPrecioBase(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PRECIO_ARTICULO_ID')
    articulo = models.ForeignKey('Articulos', db_column='ARTICULO_ID')
    precio_empresa = models.ForeignKey('PrecioEmpresa', db_column='PRECIO_EMPRESA_ID')
    moneda =  models.ForeignKey('Moneda', db_column='MONEDA_ID')
    precio              = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=6, db_column='PRECIO')

    class Meta:
        db_table = u'precios_articulos'
        abstract = True

class AlmacenBase(models.Model):
    ALMACEN_ID = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')

    class Meta:
        db_table = u'almacenes'
        abstract = True

class PrecioEmpresaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='PRECIO_EMPRESA_ID')
    nombre = models.CharField(default='N', max_length=30, db_column='NOMBRE')
    
    class Meta:
        db_table = u'PRECIOS_EMPRESA'
        abstract = True


class ArticuloDiscretoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='ART_DISCRETO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE')
    articulo = models.ForeignKey('Articulos', db_column='ARTICULO_ID')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)
    
    class Meta:
        db_table = u'articulos_discretos'
        abstract = True

class ArticuloDiscretoExistenciaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='EXIS_DISCRETO_ID')
    articulo_discreto = models.ForeignKey('ArticulosDiscretos', db_column='ART_DISCRETO_ID')
    almacen = models.ForeignKey('Almacenes', db_column='ALMACEN_ID')
    existencia = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='EXISTENCIA')
    
    class Meta:
        db_table = u'exis_discretos'
        abstract = True