#encoding:utf-8
from django.db import models
from datetime import datetime

class PuntoVentaDocumentoBase(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_PV_ID')
    caja                    = models.ForeignKey('Caja', db_column='CAJA_ID')
    cajero                  = models.ForeignKey('Cajero', db_column='CAJERO_ID')
    cliente                 = models.ForeignKey('Cliente', db_column='CLIENTE_ID', related_name='cliente')
    cliente_fac             = models.ForeignKey('Cliente', db_column='CLIENTE_FAC_ID', related_name='cliente_factura')
    direccion_cliente       = models.ForeignKey('DirCliente', db_column='DIR_CLI_ID')
    almacen                 = models.ForeignKey('Almacenes', db_column='ALMACEN_ID')
    moneda                  = models.ForeignKey('Moneda', db_column='MONEDA_ID')
    vendedor                = models.ForeignKey('Vendedor', db_column='VENDEDOR_ID')
    impuesto_sustituido     = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID', related_name='impuesto_sustituido')
    impuesto_sustituto      = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID', related_name='impuesto_sustituto')

    tipo                    = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    folio                   = models.CharField(max_length=9, db_column='FOLIO')
    fecha                   = models.DateField(db_column='FECHA')
    hora                    = models.TimeField(db_column='HORA')
    clave_cliente           = models.CharField(max_length=20, db_column='CLAVE_CLIENTE')
    clave_cliente_fac       = models.CharField(max_length=20, db_column='CLAVE_CLIENTE_FAC')
    impuesto_incluido       = models.CharField(default='S', max_length=1, db_column='IMPUESTO_INCLUIDO')
    tipo_cambio             = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    tipo_descuento          = models.CharField(default='P',max_length=1, db_column='TIPO_DSCTO')
    porcentaje_descuento    = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='DSCTO_PCTJE')
    importe_descuento       = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='DSCTO_IMPORTE')
    estado                  = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    aplicado                = models.CharField(default='S', max_length=1, db_column='APLICADO')
    importe_neto            = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    total_impuestos         = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')

    importe_donativo        = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_DONATIVO')
    total_fpgc              = models.DecimalField(max_digits=15, decimal_places=2, db_column='TOTAL_FPGC')
        
    ticket_emitido          = models.CharField(default='N', max_length=1, db_column='TICKET_EMITIDO')
    forma_emitida           = models.CharField(default='N', max_length=1, db_column='FORMA_EMITIDA')
    forma_global_emitida    = models.CharField(default='N', max_length=1, db_column='FORMA_GLOBAL_EMITIDA')
    contabilizado           = models.CharField(default='N', max_length=1, db_column='CONTABILIZADO')

    sistema_origen          = models.CharField(default='PV', max_length=2, db_column='SISTEMA_ORIGEN')
    cargar_sun              = models.CharField(default='S', max_length=1, db_column='CARGAR_SUN')
    persona                 = models.CharField(max_length=50, db_column='PERSONA')
    refer_reting            = models.CharField(blank=True, null=True, max_length=50, db_column='REFER_RETING')
    unidad_comprom          = models.CharField(default='N', max_length=1, db_column='UNID_COMPROM')    
    descripcion             = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    
    es_cfd                  = models.CharField(default='N', max_length=1, db_column='ES_CFD')
    modalidad_facturacion   = models.CharField(max_length=10, db_column='MODALIDAD_FACTURACION')
    enviado                 = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    email_envio             = models.EmailField(blank=True, null=True, db_column='EMAIL_ENVIO')
    fecha_envio             = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ENVIO')

    #Factura global
    # tipo_gen_fac = models.CharField(default='N',blank=True, null=True, max_length=1, db_column='TIPO_GEN_FAC')
    # es_fac_global = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='ES_FAC_GLOBAL')
    # fecha_ini_fac_global = models.DateField(blank=True, null=True, db_column='FECHA_INI_FAC_GLOBAL')
    # fecha_fin_fac_global = models.DateField(blank=True, null=True, db_column='FECHA_FIN_FAC_GLOBAL')
    
    usuario_creador         = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion      = models.DateTimeField(default=datetime.now().replace(hour=0), db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion    = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif     = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif       = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    usuario_cancelacion     = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion   = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
    
    class Meta:
        db_table = u'doctos_pv'
        abstract = True

class PuntoVentaDocumentoDetalleBase(models.Model):
    id                      = models.AutoField(primary_key=True, db_column='DOCTO_PV_DET_ID')
    documento_pv            = models.ForeignKey('Docto_PV', db_column='DOCTO_PV_ID')
    articulo                = models.ForeignKey('Articulos', on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    vendedor                = models.ForeignKey('Vendedor', blank=True, null=True, db_column='VENDEDOR_ID')

    clave_articulo          = models.CharField(max_length=20, db_column='CLAVE_ARTICULO')
    unidades                = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    unidades_dev            = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES_DEV')
    precio_unitario         = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    precio_unitario_impto   = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO_IMPTO')
    fpgc_unitario           = models.DecimalField(max_digits=18, decimal_places=6, db_column='FPGC_UNITARIO')
    porcentaje_descuento    = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    precio_total_neto       = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')
    precio_modificado       = models.CharField(default='N', max_length=1, db_column='PRECIO_MODIFICADO')
    porcentaje_comis        = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_COMIS')
    rol                     = models.CharField(max_length=1, db_column='ROL')
    notas                   = models.TextField(blank=True, null=True, db_column='NOTAS')
    es_tran_elect           = models.CharField(default='N', max_length=1, db_column='ES_TRAN_ELECT')
    estatus_tran_elect      = models.CharField(max_length=1,blank=True, null=True, db_column='ESTATUS_TRAN_ELECT')
    posicion                = models.IntegerField(db_column='POSICION')
    puntos                  = models.IntegerField(db_column='SIC_PUNTOS')
    dinero_electronico      = models.DecimalField(default=0, blank=True, null=True, max_digits=15, decimal_places=2, db_column='SIC_DINERO_ELECTRONICO')

    class Meta:
        db_table = u'doctos_pv_det'
        abstract = True

class PuntoVentaDocumentoLigaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_PV_LIGA_ID')
    docto_pv_fuente = models.ForeignKey('Docto_PV', related_name='fuente', db_column='DOCTO_PV_FTE_ID')
    docto_pv_destino = models.ForeignKey('Docto_PV', related_name='destino', db_column='DOCTO_PV_DEST_ID')
    
    class Meta:
        db_table = u'doctos_pv_ligas'
        abstract = True

class PuntoVentaDocumentoLigaDetalleManager(models.Manager):
    def get_by_natural_key(self, documento_liga,  detalle_fuente, detalle_destino):
        return self.get(documento_liga=documento_liga, detalle_fuente=detalle_fuente, detalle_destino=detalle_destino,)

class PuntoVentaDocumentoLigaDetalleBase(models.Model):    
    objects = PuntoVentaDocumentoLigaDetalleManager()
    documento_liga = models.ForeignKey('DoctoPVLiga', related_name='liga', db_column='DOCTO_PV_LIGA_ID')
    detalle_fuente = models.ForeignKey('Docto_pv_det', related_name='fuente', db_column='DOCTO_PV_DET_FTE_ID')
    detalle_destino = models.ForeignKey('Docto_pv_det', related_name='destino', db_column='DOCTO_PV_DET_DEST_ID')

    class Meta:
        db_table = u'doctos_pv_ligas_det'
        unique_together = (('documento_liga', 'detalle_fuente','detalle_destino',),)
        abstract = True

class PuntoVentaDocumentoDetalleTransferenciaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_PV_DET_ID')
    caja = models.ForeignKey('Caja', db_column='CAJA_ID')
    cajero = models.ForeignKey('Cajero', db_column='CAJERO_ID')
    params_text         = models.TextField(db_column='PARAMS_TEXT')
    clave_servicio      = models.CharField(max_length=10, db_column='CLAVE_SERVICIO')
    fecha               = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA')
    clave_receptor      = models.CharField(max_length=20, db_column='CLAVE_RECEPTOR')
    importe             = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    costo               = models.DecimalField(max_digits=15, decimal_places=2, db_column='COSTO')
    autorizacion        = models.CharField(max_length=20, db_column='AUTORIZACION')
    fechahora_creacion  = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CREACION')
    
    class Meta:
        db_table = u'doctos_pv_det_tran_elect'
        abstract = True

class PuntoVentaCobroBase(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='DOCTO_PV_COBRO_ID')
    tipo                = models.CharField(max_length=1, db_column='TIPO')
    documento_pv        = models.ForeignKey('Docto_PV', db_column='DOCTO_PV_ID')
    forma_cobro         = models.ForeignKey('Forma_cobro', db_column='FORMA_COBRO_ID')
    importe             = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE')
    tipo_cambio         = models.DecimalField(max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    importe_mon_doc     = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_MON_DOC')
    
    class Meta:
        db_table = u'doctos_pv_cobros'
        abstract = True

class PuntoVentaCobroReferenciaBase(models.Model):
    referencia             = models.CharField(max_length=30, db_column='REFERENCIA')
    cobro_pv = models.ForeignKey('Docto_pv_cobro', db_column='DOCTO_PV_COBRO_ID')
    forma_cobro_refer = models.ForeignKey('Forma_cobro_refer', db_column='FORMA_COBRO_REFER_ID')
    
    class Meta:
        db_table = u'doctos_pv_cobros_refer'
        abstract = True

class PuntoVentaDocumentoImpuestoManager(models.Manager):
    def get_by_natural_key(self, documento_pv,  impuesto):
        return self.get(documento_pv=documento_pv, impuesto=impuesto,)

class PuntoVentaDocumentoImpuestoBase(models.Model):
    objects = PuntoVentaDocumentoImpuestoManager()

    documento_pv        = models.ForeignKey('Docto_PV', db_column='DOCTO_PV_ID')
    impuesto            = models.ForeignKey('Impuesto', db_column='IMPUESTO_ID')
    venta_neta          = models.DecimalField(max_digits=15, decimal_places=2, db_column='VENTA_NETA')
    otros_impuestos     = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos= models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')
    importe_impuesto    = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_pv'
        unique_together = (('documento_pv', 'impuesto',),)
        abstract = True

class PuntoVentaDocumentoImpuestoGravadoBase(models.Model):
    impuesto_gravado    = models.DecimalField(max_digits=18, decimal_places=6, db_column='IMPUESTO_GRAVADO')
    listo               = models.CharField(max_length=1, default='N', db_column='LISTO')
    documento_pv        = models.ForeignKey('Docto_PV', db_column='DOCTO_PV_ID')
    articulo            = models.ForeignKey('Articulos', on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto            = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID', related_name='impuesto')
    impuesto_grav       = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_GARV_ID', related_name='impuesto_grav')

    class Meta:
        db_table = u'impuestos_grav_doctos_pv'
        abstract = True