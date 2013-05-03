#encoding:utf-8
from django.db import models
from models import *
from microsip_web.apps.inventarios.models import *


################################################################
####                                                        ####
####        MODELOS EXTRA A BASE DE DATOS MICROSIP          ####
####                                                        ####
################################################################

class Libres_linea_articulos(models.Model):
    linea 		= models.ForeignKey(LineaArticulos)
    puntos      = models.IntegerField()

    def __unicode__(self):
        return '%s'% self.id

class Libres_grupo_lineas(models.Model):
    grupo 		= models.ForeignKey(GrupoLineas)
    puntos      = models.IntegerField()

    def __unicode__(self):
    	return '%s'% self.id