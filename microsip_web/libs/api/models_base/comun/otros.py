#encoding:utf-8
from django.db import models

class PaisBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='PAIS_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    nombre_abreviado = models.CharField(max_length=10, db_column='NOMBRE_ABREV')
    
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    class Meta:
        db_table = u'paises'
        abstract = True

class EstadoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='ESTADO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    pais = models.ForeignKey('Pais', blank=True, null=True,db_column='PAIS_ID')
    nombre_abreviado = models.CharField(max_length=10, db_column='NOMBRE_ABREV')
    
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    class Meta:
        db_table = u'estados'
        abstract = True

class CiudadBase(models.Model):

    id          = models.AutoField(primary_key=True, db_column='CIUDAD_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    estado      = models.ForeignKey('Estado', db_column='ESTADO_ID')
    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')
   
    class Meta:
        db_table = u'ciudades'
        abstract = True

class MonedaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='MONEDA_ID')
    es_moneda_local = models.CharField(default='N', max_length=1, db_column='ES_MONEDA_LOCAL')
    nombre = models.CharField(max_length=30, db_column='NOMBRE')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')
    
    class Meta:
        db_table = u'monedas'
        abstract = True

class TipoCambioBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='HISTORIA_CAMB_ID')
    moneda = models.ForeignKey('Moneda', db_column='MONEDA_ID')
    fecha = models.DateField(db_column='FECHA')
    tipo_cambio = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    tipo_cambio_cobros = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO_COBROS')

    usuario_creador = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'historia_cambiaria'
        abstract = True

class ViaEmbarqueBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='VIA_EMBARQUE_ID')
    nombre = models.CharField(max_length=20, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'vias_embarque'
        abstract = True

class FolioVentaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIO_VENTAS_ID')
    tipo_doc = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    serie = models.CharField(max_length=3, db_column='SERIE')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')
    modalidad_facturacion = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    punto_reorden = models.IntegerField(db_column='PUNTO_REORDEN_FOLIOS')
    dias_reorden = models.IntegerField(db_column='DIAS_REORDEN_FOLIOS')
    
    class Meta:
        db_table = u'folios_ventas'
        abstract = True

class FolioCompraBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIO_COMPRAS_ID')
    tipo_doc = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    serie = models.CharField(max_length=3, db_column='SERIE')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')
      
    class Meta:
        db_table = u'folios_compras'
        abstract = True

        