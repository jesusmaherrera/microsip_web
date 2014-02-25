#encoding:utf-8
from django.db import models

class InventariosConcepto(models.Model):
    id = models.AutoField( primary_key = True, db_column= 'CONCEPTO_IN_ID' )
    nombre_abrev = models.CharField( max_length = 30, db_column = 'NOMBRE_ABREV' )
    naturaleza = models.CharField(max_length=1, db_column='NATURALEZA')
    folio_autom = models.CharField( default = 'N', max_length = 1, db_column = 'FOLIO_AUTOM' )
    sig_folio = models.CharField( max_length = 9, db_column = 'SIG_FOLIO' )

    class Meta:
        db_table = u'conceptos_in'
        abstract = True

class InventariosCentroCostosBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='CENTRO_COSTO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_predet = models.CharField(default='N', max_length=1, db_column='ES_PREDET')
    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'centros_costo'
        abstract = True


