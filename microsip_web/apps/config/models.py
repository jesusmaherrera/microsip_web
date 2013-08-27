from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True, db_column='USUARIO_ID')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    tipo = models.CharField(max_length=1, db_column='TIPO')
    acceso_empresas = models.CharField(max_length=1, db_column='ACCESO_EMPRESAS')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'usuarios'

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
        