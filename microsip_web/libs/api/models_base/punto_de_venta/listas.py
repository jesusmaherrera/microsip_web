#encoding:utf-8
from django.db import models

class CajeroBase(models.Model):
    id          = models.AutoField(primary_key=True, db_column='CAJERO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    usuario     = models.CharField(max_length=31, db_column='USUARIO')

    class Meta:
        db_table = u'cajeros'
        abstract = True

class CajaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='CAJA_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    
    class Meta:
        db_table = u'cajas'
        abstract = True

class FormaCobroBase(models.Model):
    id          = models.AutoField(primary_key=True, db_column='FORMA_COBRO_ID')
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    tipo        = models.CharField(max_length=1, default='E', db_column='TIPO')
    
    class Meta:
        db_table = u'formas_cobro'
        abstract = True

class FormaCobroReferenciaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='FORMA_COBRO_REFER_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    forma_cobro = models.ForeignKey('Forma_cobro', db_column='FORMA_COBRO_ID')

    class Meta:
        db_table = u'formas_cobro_refer'
        abstract = True