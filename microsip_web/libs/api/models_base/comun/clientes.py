#encoding:utf-8
from django.db import models

class ClienteTipoBase(models.Model):
    id = models.AutoField( primary_key = True, db_column = 'TIPO_CLIENTE_ID' )
    nombre = models.CharField( max_length = 100, db_column = 'NOMBRE' )
     
    class Meta:
        db_table = u'tipos_clientes'
        abstract = True

class CondicionPagoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='COND_PAGO_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    dias_ppag = models.PositiveSmallIntegerField(default=0, db_column='DIAS_PPAG')
    porcentaje_descuento_ppago = models.PositiveSmallIntegerField(default=0, db_column='PCTJE_DSCTO_PPAG')

    SI_O_NO = (('S', 'Si'),('N', 'No'),)
    es_predet = models.CharField(default='N', max_length=1, choices=SI_O_NO ,db_column='ES_PREDET')

    usuario_creador = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_CREADOR')
    fechahora_creacion = models.DateTimeField(auto_now_add=True, db_column='FECHA_HORA_CREACION')
    usuario_aut_creacion = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_CREACION')
    usuario_ult_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_ULT_MODIF')
    fechahora_ult_modif = models.DateTimeField(auto_now = True, db_column='FECHA_HORA_ULT_MODIF')
    usuario_aut_modif = models.CharField(blank=True, null=True, max_length=31, db_column='USUARIO_AUT_MODIF')
    
    class Meta:
        db_table = u'condiciones_pago'
        abstract = True

class CondicionPagoPlazoBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='PLAZO_COND_PAG_ID')
    condicion_de_pago = models.ForeignKey('CondicionPago', db_column='COND_PAGO_ID')
    dias = models.PositiveSmallIntegerField( db_column='DIAS_PLAZO')
    porcentaje_de_venta = models.PositiveSmallIntegerField( db_column='PCTJE_VEN')
    
    class Meta:
        db_table = u'plazos_cond_pag'
        abstract = True

class ClienteBase( models.Model ):
    id = models.AutoField( primary_key = True, db_column = 'CLIENTE_ID' )

    nombre = models.CharField( max_length = 100, db_column = 'NOMBRE' )
    estatus = models.CharField( default = 'A',  max_length = 1, db_column = 'ESTATUS' )
    cuenta_xcobrar = models.CharField( max_length = 9, db_column = 'CUENTA_CXC' )
    usuario_ult_modif = models.CharField( blank = True, null = True, max_length = 31, db_column = 'USUARIO_ULT_MODIF' )
    fechahora_ult_modif = models.DateTimeField( auto_now = True, blank = True, null = True, db_column = 'FECHA_HORA_ULT_MODIF' )
    SI_O_NO = (('S', 'Si'),)
    cobrar_impuestos = models.CharField(default='S', max_length=1, choices=SI_O_NO ,db_column='COBRAR_IMPUESTOS')
    generar_interereses = models.CharField(default='S', max_length=1, choices=SI_O_NO ,db_column='GENERAR_INTERESES')
    emir_estado_cuenta = models.CharField(default='S', max_length=1, choices=SI_O_NO ,db_column='EMITIR_EDOCTA')

    moneda = models.ForeignKey('Moneda', db_column = 'MONEDA_ID' )
    tipo_cliente = models.ForeignKey( 'TipoCliente', blank = True, null = True, db_column = 'TIPO_CLIENTE_ID' )
    condicion_de_pago = models.ForeignKey('CondicionPago', db_column='COND_PAGO_ID')
    
    class Meta:
        db_table = u'clientes'
        abstract = True

class ClienteClaveRolBase(models.Model):
    id      = models.AutoField(primary_key=True, db_column='ROL_CLAVE_CLI_ID')
    nombre  = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    class Meta:
        db_table = u'roles_claves_clientes'
        abstract = True

class ClienteClaveBase(models.Model):
    id      = models.AutoField(primary_key=True, db_column='CLAVE_CLIENTE_ID')
    clave   = models.CharField(max_length=20, db_column='CLAVE_CLIENTE')
    cliente = models.ForeignKey('Cliente', db_column='CLIENTE_ID')
    rol = models.ForeignKey('RolClavesClientes', db_column='ROL_CLAVE_CLI_ID')

    class Meta:
        db_table = u'claves_clientes'
        abstract = True

class ClienteDireccionBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='DIR_CLI_ID')
    nombre_consignatario = models.CharField(max_length=18, db_column='NOMBRE_CONSIG')
    rfc_curp = models.CharField(max_length=18, db_column='RFC_CURP', blank=True, null=True)
    
    #Direccion
    calle = models.CharField(blank=True, null=True, max_length=430, db_column='CALLE')
    calle_nombre = models.CharField(blank=True, null=True, max_length=100, db_column='NOMBRE_CALLE')
    numero_exterior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_EXTERIOR')
    numero_interior = models.CharField(blank=True, null=True, max_length=10, db_column='NUM_INTERIOR')
    colonia = models.CharField(blank=True, null=True, max_length=100, db_column='COLONIA')
    poblacion = models.CharField(blank=True, null=True, max_length=100, db_column='POBLACION')
    referencia = models.CharField(blank=True, null=True, max_length=100, db_column='REFERENCIA')
    codigo_postal = models.CharField(blank=True, null=True, max_length=10, db_column='CODIGO_POSTAL')
    email = models.EmailField(blank=True, null=True, db_column='EMAIL')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_DIR_PPAL')

    cliente = models.ForeignKey('Cliente', db_column='CLIENTE_ID')
    ciudad = models.ForeignKey('Ciudad', db_column='CIUDAD_ID')
    estado = models.ForeignKey('Estado', db_column='ESTADO_ID', blank=True, null=True)
    pais = models.ForeignKey('Pais', db_column='PAIS_ID', blank=True, null=True)

    class Meta:
        db_table = u'dirs_clientes'
        abstract = True

class libreClienteBase(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLIENTE_ID')

    class Meta:
        db_table = u'libres_clientes'
        abstract = True