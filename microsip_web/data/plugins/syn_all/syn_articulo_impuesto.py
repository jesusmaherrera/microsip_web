#encoding:utf-8
'''
    Plugin para:
        Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. 
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import post_save
from django.dispatch import receiver

from ....libs.api.models import Articulo, ImpuestosArticulo, Impuesto
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(post_save, sender=ImpuestosArticulo)
def SincronizarArticuloImpuesto(sender, **kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        articulo_impuesto_a_syncronizar =  kwargs.get('instance')
        articulo_nombre = articulo_impuesto_a_syncronizar.articulo.nombre
        
        indice, indice_final = get_indices(len(bases_de_datos), 40,'ARTICULO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            articulo = Articulo.objects.using(base_de_datos).get(nombre=articulo_nombre)
                
            primer_impuesto = first_or_none(ImpuestosArticulo.objects.using(base_de_datos).filter(articulo=articulo))
            impuesto = Impuesto.objects.using(base_de_datos).get(nombre=articulo_impuesto_a_syncronizar.impuesto.nombre)

            if primer_impuesto:
                primer_impuesto.impuesto = impuesto
                primer_impuesto.save(using=base_de_datos)
            else:
                ImpuestosArticulo.objects.using(base_de_datos).create(
                            articulo = articulo,
                            impuesto = impuesto,
                        )
                
        # set_indices(indice_final, len(bases_de_datos), 'ARTICULO')