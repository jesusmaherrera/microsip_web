#encoding:utf-8
from django.db import models
from datetime import datetime

class ComprasDocumentoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_ID')
    tipo = models.CharField(max_length=1, db_column='TIPO_DOCTO')
    subtipo = models.CharField(blank=True, null=True, max_length=1, db_column='SUBTIPO_DOCTO')
    folio = models.CharField(max_length=9, db_column='FOLIO')
    fecha = models.DateField(default=datetime.now, db_column='FECHA')
    
    proveedor_clave = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_PROV')
    proveedor = models.ForeignKey('Proveedor', db_column='PROVEEDOR_ID')
    proveedor_folio = models.CharField(blank=True, null=True, max_length=9, db_column='FOLIO_PROV')
    factura_dev = models.CharField(blank=True, null=True, max_length=9, db_column='FACTURA_DEV')
    consignatario = models.ForeignKey('ConsignatarioCompras', blank=True, null=True, db_column='CONSIG_CM_ID')
    almacen = models.ForeignKey('Almacenes',  db_column='ALMACEN_ID')
    # default=lambda: firstALMACENid_or_none(Almacenes.objects.filter(es_predet='S'))
    pedimento = models.ForeignKey('Pedimento', blank=True, null=True, db_column='PEDIMENTO_ID')
    moneda = models.ForeignKey('Moneda', db_column='MONEDA_ID')
    #  default=lambda:firstid_or_none(Moneda.objects.filter(es_predet='S'))
    tipo_cambio = models.DecimalField(default=1, max_digits=18, decimal_places=6, db_column='TIPO_CAMBIO')
    
    tipo_descuento = models.CharField(default='P',max_length=1, db_column='TIPO_DSCTO')
    porcentaje_descuento = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='DSCTO_PCTJE')
    importe_descuento = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='DSCTO_IMPORTE')
    
    estado = models.CharField(default='N', max_length=1, db_column='ESTATUS')
    aplicado = models.CharField(default='S', max_length=1, db_column='APLICADO')
    fecha_entrega = models.DateField(blank=True, null=True, db_column='FECHA_ENTREGA')
    descripcion = models.CharField(blank=True, null=True, max_length=200, db_column='DESCRIPCION')
    importe_neto = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_NETO')
    fletes = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='FLETES')
    otros_cargos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='OTROS_CARGOS')
    total_impuestos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_IMPUESTOS')
    total_retenciones = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_RETENCIONES')
    gastos_aduanales = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='GASTOS_ADUANALES')
    otros_gastos = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='OTROS_GASTOS')
    total_fpgc = models.DecimalField(default=0, max_digits=15, decimal_places=2, db_column='TOTAL_FPGC')

    forma_emitida = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='FORMA_EMITIDA')
    contabilizado = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='CONTABILIZADO')
    acreditar_cxp = models.CharField(default='N', blank=True, null=True, max_length=1, db_column='ACREDITAR_CXP')
    sistema_origen = models.CharField(default='CM', max_length=2, db_column='SISTEMA_ORIGEN')
    condicion_pago = models.ForeignKey('CondicionPagoCp', db_column='COND_PAGO_ID')
    fecha_dscto_ppag = models.DateField(blank=True, null=True, db_column='FECHA_dscto_ppag')
    porcentaje_dscto_ppag = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PPAG')
    via_embarque = models.ForeignKey('ViaEmbarque', blank=True, null=True, db_column='VIA_EMBARQUE_ID')
    impuesto_sustituido = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUIDO_ID', related_name='impuesto_sustituidoID')
    impuesto_sustituto = models.ForeignKey('Impuesto', on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_SUSTITUTO_ID', related_name='impuesto_sustitutoID')
    cargar_sun = models.CharField(default='S', max_length=1, db_column='CARGAR_SUN')
    enviado = models.CharField(default='N', max_length=1, db_column='ENVIADO')
    envio_fechahora = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_ENVIO')
    envio_email = models.EmailField(blank=True, null=True, db_column='EMAIL_ENVIO')
    tiene_cfd = models.CharField(default='N', max_length=1, db_column='TIENE_CFD')

    usuario_creador = models.CharField(max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now=True, blank=True, null=True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    usuario_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CANCELACION')
    fechahora_cancelacion = models.DateTimeField(blank=True, null=True, db_column='FECHA_HORA_CANCELACION')
    usuario_aut_cancelacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CANCELACION')
        
    class Meta:
        db_table = u'doctos_cm'
        abstract = True

class ComprasDocumentoCargoVencimientoBase(models.Model):
    documento = models.ForeignKey('DocumentoCompras', unique_for_date='fecha', db_column='DOCTO_CM_ID')
    fecha = models.DateField(db_column='FECHA_VENCIMIENTO') 
    porcentaje_de_venta = models.PositiveSmallIntegerField( db_column='PCTJE_VEN')

    class Meta:
        db_table = u'vencimientos_cargos_cm'
        abstract = True

class ComprasDocumentoDetalleBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_DET_ID')
    documento = models.ForeignKey('DocumentoCompras', db_column='DOCTO_CM_ID')

    clave_articulo = models.CharField(blank=True, null=True, max_length=20, db_column='CLAVE_ARTICULO')
    articulo = models.ForeignKey('Articulos', on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    unidades = models.DecimalField(max_digits=18, decimal_places=5, db_column='UNIDADES')
    unidades_rec_dev = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='UNIDADES_REC_DEV')
    unidades_a_rec = models.DecimalField(default=0, max_digits=18, decimal_places=5, db_column='UNIDADES_A_REC')
    umed = models.CharField(blank=True, null=True, max_length=20, db_column='UMED')
    contenido_umed = models.DecimalField(default=1, max_digits=18, decimal_places=5, db_column='CONTENIDO_UMED')
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=6, db_column='PRECIO_UNITARIO')
    fpgc_unitario = models.DecimalField(default=0, max_digits=18, decimal_places=6, db_column='FPGC_UNITARIO')
    porcentaje_descuento = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO')
    porcentaje_descuento_pro = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PRO')
    porcentaje_descuento_vol = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_VOL')
    porcentaje_descuento_promo = models.DecimalField(default=0,max_digits=9, decimal_places=6, db_column='PCTJE_DSCTO_PROMO')
    precio_total_neto = models.DecimalField(max_digits=15, decimal_places=2, db_column='PRECIO_TOTAL_NETO')

    porcentaje_arancel = models.DecimalField(default=0, max_digits=9, decimal_places=6, db_column='PCTJE_ARANCEL')
    notas = models.TextField(blank=True, null=True, db_column='NOTAS')
    posicion = models.IntegerField(default=0)

    class Meta:
        db_table = u'doctos_cm_det'
        abstract = True

class ComprasDocumentoImpuestoManager(models.Manager):
    def get_by_natural_key(self, documento,  impuesto):
        return self.get(documento= documento, impuesto= impuesto,)

class ComprasDocumentoImpuestoBase(models.Model):
    objects = ComprasDocumentoImpuestoManager()
    documento = models.ForeignKey('DocumentoCompras', db_column='DOCTO_CM_ID')
    impuesto = models.ForeignKey('Impuesto', db_column='IMPUESTO_ID')
    compra_neta = models.DecimalField(max_digits=15, decimal_places=2, db_column='COMPRA_NETA')
    otros_impuestos = models.DecimalField(max_digits=15, decimal_places=2, db_column='OTROS_IMPUESTOS')
    porcentaje_impuestos = models.DecimalField(max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')
    importe_impuesto = models.DecimalField(max_digits=15, decimal_places=2, db_column='IMPORTE_IMPUESTO')
    
    class Meta:
        db_table = u'impuestos_doctos_cm'
        abstract = True
        unique_together = (('documento', 'impuesto',),)

class ComprasDocumentoLigaBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DOCTO_CM_LIGA_ID')
    documento_fte = models.ForeignKey('DocumentoCompras', related_name='fuente', db_column='DOCTO_CM_FTE_ID')  
    documento_dest = models.ForeignKey('DocumentoCompras', related_name='destino', db_column='DOCTO_CM_DEST_ID')  

    class Meta:
        db_table = u'doctos_cm_ligas'
        abstract = True

class ComprasDocumentoLigaDetalleManager(models.Manager):
    def get_by_natural_key(self, documento_liga,  detalle_fuente, detalle_destino):
        return self.get(documento_liga=documento_liga, detalle_fuente=detalle_fuente, detalle_destino=detalle_destino,)

class ComprasDocumentoLigaDetalleBase(models.Model):
    objects = ComprasDocumentoLigaDetalleManager()
    documento_liga = models.ForeignKey('DocumentoComprasLiga', related_name='liga', db_column='DOCTO_CM_LIGA_ID')
    detalle_fuente = models.ForeignKey('DocumentoComprasDetalle', related_name='fuente', db_column='DOCTO_CM_DET_FTE_ID')
    detalle_destino = models.ForeignKey('DocumentoComprasDetalle', related_name='destino', db_column='DOCTO_CM_DET_DEST_ID')

    class Meta:
        db_table = u'doctos_cm_ligas_det'
        unique_together = (('documento_liga', 'detalle_fuente','detalle_destino',),)
        abstract = True

class ComprasConsignatarioBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='CONSIG_CM_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')

    calle = models.CharField(blank=True, null=True, max_length=430, db_column='CALLE')
    calle_nombre = models.CharField(blank=True, null=True, max_length=100, db_column='NOMBRE_CALLE')
    numero_exterior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_EXTERIOR')
    numero_interior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_INTERIOR')
    colonia = models.CharField(blank=True, null=True, max_length=100, db_column='COLONIA')
    poblacion = models.CharField(blank=True, null=True, max_length=100, db_column='POBLACION')
    referencia = models.CharField(blank=True, null=True, max_length=100, db_column='REFERENCIA')
    ciudad = models.ForeignKey('Ciudad', db_column='CIUDAD_ID')
    estado = models.ForeignKey('Estado', db_column='ESTADO_ID', blank=True, null=True)
    codigo_postal = models.CharField(blank=True, null=True, max_length=10, db_column='CODIGO_POSTAL')
    pais = models.ForeignKey('Pais', db_column='PAIS_ID', blank=True, null=True)

    telefono1 = models.CharField(blank=True, null=True, max_length=10, db_column='TELEFONO1')
    telefono2 = models.CharField(blank=True, null=True, max_length=10, db_column='TELEFONO2')
    fax = models.CharField(blank=True, null=True, max_length=10, db_column='FAX')
    email = models.CharField(blank=True, null=True, max_length=200, db_column='EMAIL')
    contacto = models.CharField(blank=True, null=True, max_length=200, db_column='CONTACTO')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')

    class Meta:
        db_table = u'consignatarios_cm'
        abstract = True