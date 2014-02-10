#encoding:utf-8
from django.db import models
from django.db import router

class GrupoLineas(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='GRUPO_LINEA_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    
    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(GrupoLineas, self).save(*args, **kwargs) 

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'grupos_lineas'
        abstract  = True

class LineaArticulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='LINEA_ARTICULO_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(LineaArticulos, self).save(*args, **kwargs) 
        
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'lineas_articulos'
        abstract  = True

class Articulos( models.Model ):
    id = models.AutoField( primary_key = True, db_column = 'ARTICULO_ID' )
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

    def save(self, *args, **kwargs):    
        using = kwargs.get('using', None)
        using = using or router.db_for_write(self.__class__, instance=self)

        if self.id == None:
            self.id = next_id('ID_CATALOGOS', using)  
       
        super(Articulo, self).save(*args, **kwargs) 
        
    def __unicode__( self) :
        return u'%s (%s)' % ( self.nombre, self.unidad_venta )

    class Meta:
        db_table = u'articulos'
        abstract  = True