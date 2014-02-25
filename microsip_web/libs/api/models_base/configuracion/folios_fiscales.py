#encoding:utf-8
from django.db import models

class ConfiguracionFolioFiscalBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='FOLIOS_FISCALES_ID')
    serie = models.CharField(max_length=3, db_column='SERIE')
    folio_ini = models.IntegerField(db_column='FOLIO_INI')
    folio_fin = models.IntegerField(db_column='FOLIO_FIN')
    ultimo_utilizado = models.IntegerField(db_column='ULTIMO_UTILIZADO')
    num_aprobacion = models.CharField(max_length=14, db_column='NUM_APROBACION')
    ano_aprobacion = models.IntegerField(db_column='ANO_APROBACION')
    modalidad_facturacion = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    fecha_aprobacion = models.DateField(db_column='FECHA_APROBACION', blank=True, null=True)
    fecha_vencimiento = models.DateField(db_column='FECHA_VENCIMIENTO', blank=True, null=True)
    
    class Meta:
        db_table =u'folios_fiscales'
        abstract = True

class ConfiguracionFolioFiscalUsoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='USO_FOLIO_ID')
    folios_fiscales = models.ForeignKey('FoliosFiscales', db_column='FOLIOS_FISCALES_ID')
    folio = models.IntegerField(db_column='FOLIO')
    fecha = models.DateField(db_column='FECHA')
    sistema = models.CharField(max_length=2, db_column='SISTEMA')
    documento = models.IntegerField(db_column='DOCTO_ID')
    xml = models.TextField(db_column='XML')
    prov_cert = models.CharField(max_length=20, db_column='PROV_CERT')
    fechahora_timbrado = models.CharField(max_length=25, db_column='FECHA_HORA_TIMBRADO')
    uuid = models.CharField(max_length=45, db_column='UUID')
    
    class Meta:
        db_table =u'usos_folios_fiscales'
        abstract = True