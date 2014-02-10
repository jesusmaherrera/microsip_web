from django.db import models
from microsip_web.libs.api.models import *



#############################################################################################################################################################
##################################################MODELOS DE APLICACION DJANGO###############################################################################
#############################################################################################################################################################

class InformacionContable_C(models.Model):
    cuenta_proveedores  = models.ForeignKey(CuentaCo)
    
    def __unicode__(self):
        return u'%s'% self.id

    class Meta:
	 	db_table = u'sic_c_informacioncontable'