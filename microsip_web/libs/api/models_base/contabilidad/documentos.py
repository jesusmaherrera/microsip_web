#encoding:utf-8
from django.db import models

class ContabilidadGrupoPolizaPeriodoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='GRUPO_POL_PERIOD_ID')

    class Meta:
        db_table = 'grupos_polizas_period_co'
        abstract = True

class ContabilidadRecordatorioBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='RECORDATORIO_ID')
    
    class Meta:
        db_table = u'recordatorios'
        abstract = True

class ContabilidadDocumentoBase(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_CO_ID')
    tipo_poliza             = models.ForeignKey('TipoPoliza', db_column='TIPO_POLIZA_ID')
    poliza                  = models.CharField(max_length=9, db_column='POLIZA')
    fecha                   = models.DateField(db_column='FECHA')
    moneda                  = models.ForeignKey('Moneda', db_column='MONEDA_ID')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    estatus                 = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    cancelado               = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    ajuste                  = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    integ_co                = models.CharField(default='S', max_length=1, db_column='INTEG_CO')
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    forma_emitida           = models.CharField(default='N', max_length=1, db_column='FORMA_EMITIDA')
    sistema_origen          = models.CharField(max_length=2, db_column='SISTEMA_ORIGEN')
    nombre                  = models.CharField(blank=True, null=True, max_length=30, db_column='NOMBRE')
    grupo_poliza_periodo    = models.ForeignKey('GrupoPolizasPeriodoCo', blank=True, null=True, db_column='GRUPO_POL_PERIOD_ID')
    integ_ba                = models.CharField(default='N', max_length=1, db_column='INTEG_BA')
    
    usuario_creador         = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')

    class Meta:
        db_table = u'doctos_co'
        abstract = True

class ContabilidadDocumentoDetalleBase(models.Model):
    id          = models.AutoField(primary_key=True, db_column='DOCTO_CO_DET_ID')
    docto_co    = models.ForeignKey('DoctoCo', db_column='DOCTO_CO_ID')
    cuenta      = models.ForeignKey('CuentaCo', db_column='CUENTA_ID')
    depto_co    = models.ForeignKey('DeptoCo', db_column='DEPTO_CO_ID')
    tipo_asiento= models.CharField(default='C', max_length=1, db_column='TIPO_ASIENTO')
    importe     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    importe_mn  = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_MN')
    ref         = models.CharField(max_length=10, db_column='REFER')
    descripcion = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    posicion    = models.IntegerField(default=0)
    recordatorio= models.ForeignKey('Recordatorio', blank=True, null=True, db_column='RECORDATORIO_ID')
    fecha       = models.DateField(db_column='FECHA')
    cancelado   = models.CharField(default='N', max_length=1, db_column='CANCELADO')
    aplicado    = models.CharField(default='N', max_length=1, db_column='APLICADO')
    ajuste      = models.CharField(default='N', max_length=1, db_column='AJUSTE')
    moneda      = models.ForeignKey('Moneda', db_column='MONEDA_ID')

    class Meta:
        db_table = u'doctos_co_det'
        abstract = True


