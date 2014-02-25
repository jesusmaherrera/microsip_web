#encoding:utf-8
from django.db import models

class TipoPolizaBase(models.Model):
    id          = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_ID')
    clave       = models.CharField(max_length=1, db_column='CLAVE')
    nombre      = models.CharField(max_length=30, db_column='NOMBRE')
    tipo_consec = models.CharField(max_length=1, db_column='TIPO_CONSEC')
    prefijo     = models.CharField(max_length=1, db_column='PREFIJO')
    
    class Meta:
        db_table = u'tipos_polizas'
        abstract = True

class TipoPolizaDetalleBase(models.Model):
    id              = models.AutoField(primary_key=True, db_column='TIPO_POLIZA_DET_ID')
    tipo_poliza     = models.ForeignKey('TipoPoliza', db_column='TIPO_POLIZA_ID')
    ano         = models.SmallIntegerField(db_column='ANO')
    mes         = models.SmallIntegerField(db_column='MES')
    consecutivo = models.IntegerField(db_column='CONSECUTIVO')
        
    class Meta:
        db_table = u'tipos_polizas_det'
        abstract = True

class ContabilidadDepartamentoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DEPTO_CO_ID')
    clave = models.CharField(max_length=1, db_column='CLAVE')

    class Meta:
        db_table = u'deptos_co'
        abstract = True