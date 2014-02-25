#encoding:utf-8
from django.db import models

class AduanaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='ADUANA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    ciudad = models.ForeignKey('Ciudad', db_column='CIUDAD_ID')
    gln = models.CharField(blank=True, null=True, max_length=20, db_column='GLN')
    es_predet = models.CharField(blank=True, null=True, max_length=20, db_column='ES_PREDET')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'aduanas'
        abstract = True

class PedimentoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='PEDIMENTO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE')
    fecha = models.DateField(db_column='FECHA', blank=True, null=True)
    aduana_nombre = models.CharField(max_length=50, db_column='ADUANA')
    aduana = models.ForeignKey('Aduana', db_column='ADUANA_ID')

    class Meta:
        db_table = u'pedimentos'
        abstract = True