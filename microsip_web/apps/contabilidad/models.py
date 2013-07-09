from django.db import models
from django.db.models.signals import pre_save
from django.core import urlresolvers
from microsip_web.apps.main.models import *



#############################################################################################################################################################
##################################################MODELOS DE APLICACION DJANGO###############################################################################
#############################################################################################################################################################

class InformacionContable_C(models.Model):
    cuenta_proveedores  = models.ForeignKey(CuentaCo)
    def __unicode__(self):
        return u'%s'% self.id