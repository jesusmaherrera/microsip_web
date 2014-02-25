#encoding:utf-8
from django.db import models
from datetime import datetime

class CuentasXCobrarConceptoBase(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='CONCEPTO_CC_ID')
    nombre_abrev        = models.CharField(max_length=30, db_column='NOMBRE_ABREV')
    crear_polizas       = models.CharField(default='N', max_length=1, db_column='CREAR_POLIZAS')
    cuenta_contable     = models.CharField(max_length=30, db_column='CUENTA_CONTABLE')
    clave_tipo_poliza   = models.CharField(max_length=1, db_column='TIPO_POLIZA')
    descripcion_poliza  = models.CharField(max_length=200, db_column='DESCRIPCION_POLIZA')
    tipo                = models.CharField(max_length=1, db_column='TIPO')

    class Meta:
        db_table = u'conceptos_cc'
        abstract = True