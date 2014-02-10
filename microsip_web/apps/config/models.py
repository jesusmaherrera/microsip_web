from django.db import models

class Configuracion(models.Model):
    id = models.AutoField(primary_key=True, db_column='ELEMENTO_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    padre = models.ForeignKey('self', related_name='padre_a', db_column='PADRE_ID')
    valor = models.CharField(default='', blank = True, null = True, max_length=100, db_column='VALOR')
    
    def save(self, *args, **kwargs):
        if not self.id:
            using = kwargs.get('using', None)
            using = using or router.db_for_write(self.__class__, instance=self)
            self.id = next_id('ID_CATALOGOS', using)

        super(Configuracion, self).save(*args, **kwargs)

    def get_value(self):
        if self.valor == '':
            return None
        return self.valor

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'registry'


class Usuario(models.Model):
    id = models.AutoField(primary_key=True, db_column='USUARIO_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    acceso_empresas = models.CharField(max_length=1, db_column='ACCESO_EMPRESAS')
    usar_rol = models.CharField(default= 'N', max_length=1, db_column='USAR_ROL')
    # rol = models.ForeignKey( 'self', db_column = 'ROL_ID', related_name = 'rol_id', blank = True, null = True )
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'usuarios'

class DerechoUsuarioManager(models.Manager):
    def get_by_natural_key(self, usuario,  clave_objeto):
        return self.get(usuario=usuario, clave_objeto=clave_objeto)
        
class DerechoUsuario(models.Model):
    objects = DerechoUsuarioManager()
    
    usuario = models.ForeignKey(Usuario, db_column='USUARIO_ID')
    clave_objeto = nombre = models.CharField(max_length=3, db_column='CLAVE_OBJETO')

    def __unicode__(self):
        return u'%s - %s' % (self.usuario, self.clave_objeto)

    class Meta:
        db_table = u'derechos_usuarios'
        unique_together = (('usuario', 'clave_objeto'),)

class Empresa(models.Model):
    id = models.AutoField(primary_key=True, db_column='EMPRESA_ID')
    nombre = models.CharField(max_length=30, db_column='NOMBRE_CORTO')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'empresas'

class EmpresaUsuarioManager(models.Manager):
    def get_by_natural_key(self, usuario, empresa):
        return self.get(usuario=usuario, empresa=empresa)

class EmpresaUsuario(models.Model):
    objects = EmpresaUsuarioManager()

    usuario = models.ForeignKey(Usuario, db_column='USUARIO_ID')
    empresa = models.ForeignKey(Empresa, db_column='EMPRESA_ID')

    def __unicode__(self):
        return u'%s - %s' % (self.usuario, self.empresa)

    def natural_key(self):
        return (self.usuario, self.empresa)

    class Meta:
        db_table = u'empresas_usuarios'
        unique_together = (('usuario', 'empresa'),)
        