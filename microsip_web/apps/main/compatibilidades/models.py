from django.db import models

class SeccionArticulos(models.Model):
    nombre  = models.CharField(max_length=30)
    seccion_padre = models.ForeignKey('self', related_name='seccion_padre_a', blank=True, null=True)

    def __unicode__(self):
        return u'%s'% self.nombre