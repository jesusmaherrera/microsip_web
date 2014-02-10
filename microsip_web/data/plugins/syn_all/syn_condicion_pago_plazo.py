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

from ....libs.api.models import CondicionPago, CondicionPagoPlazo
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(post_save, sender=CondicionPagoPlazo)
def SincronizarCondicionPagoPlazo(sender, **kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        condicion_pago_plazo_a_syncronizar =  kwargs.get('instance')
        condicion_pago_nombre = condicion_pago_plazo_a_syncronizar.condicion_de_pago.nombre
        
        indice, indice_final = get_indices(len(bases_de_datos), 100, 'CONDICIONPAGO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            condicion_de_pago = CondicionPago.objects.using(base_de_datos).get(nombre=condicion_pago_nombre)
                
            primer_plazo = first_or_none(CondicionPagoPlazo.objects.using(base_de_datos).filter(condicion_de_pago= condicion_de_pago))
            
            if primer_plazo:
                primer_plazo.dias = condicion_pago_plazo_a_syncronizar.dias
                primer_plazo.porcentaje_de_venta= condicion_pago_plazo_a_syncronizar.porcentaje_de_venta
                primer_plazo.save(using=base_de_datos)
            else:
                CondicionPagoPlazo.objects.using(base_de_datos).create(
                            condicion_de_pago = condicion_de_pago,
                            dias = condicion_pago_plazo_a_syncronizar.dias,
                            porcentaje_de_venta = condicion_pago_plazo_a_syncronizar.porcentaje_de_venta
                        )
        # set_indices(indice_final, len(bases_de_datos), 'CONDICIONPAGO')