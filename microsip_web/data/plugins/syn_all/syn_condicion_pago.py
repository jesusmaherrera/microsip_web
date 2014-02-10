#encoding:utf-8
'''
    Plugin para:
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from ....libs.api.models import CondicionPago
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=CondicionPago)
def SincronizarCondicionPago(sender, **kwargs):
    ''' Para sincronizar condiciones de pago en todas las empreas registradas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        condicion_pago_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 100, 'CONDICIONPAGO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            try:
                condicion_pago_nombre = CondicionPago.objects.using(default_db).get(pk=condicion_pago_a_syncronizar.id).nombre
            except ObjectDoesNotExist: 
                condicion_pago_nombre = condicion_pago_a_syncronizar.nombre
                
            condicion_pago = first_or_none(CondicionPago.objects.using(base_de_datos).filter(nombre=condicion_pago_nombre))
            if condicion_pago:
                condicion_pago.nombre= condicion_pago_a_syncronizar.nombre
                condicion_pago.dias_ppag= condicion_pago_a_syncronizar.dias_ppag
                condicion_pago.porcentaje_descuento_ppago= condicion_pago_a_syncronizar.porcentaje_descuento_ppago
                condicion_pago.es_predet= condicion_pago_a_syncronizar.es_predet
                condicion_pago.usuario_creador= condicion_pago_a_syncronizar.usuario_creador
                condicion_pago.usuario_ult_modif= condicion_pago_a_syncronizar.usuario_creador

                condicion_pago.save(using=base_de_datos)
            else:
                CondicionPago.objects.using(base_de_datos).create(
                        nombre= condicion_pago_a_syncronizar.nombre,
                        dias_ppag= condicion_pago_a_syncronizar.dias_ppag,
                        porcentaje_descuento_ppago= condicion_pago_a_syncronizar.porcentaje_descuento_ppago,
                        es_predet= condicion_pago_a_syncronizar.es_predet,
                        usuario_creador= condicion_pago_a_syncronizar.usuario_creador,
                        usuario_ult_modif= condicion_pago_a_syncronizar.usuario_creador
                    )
        set_indices(indice_final, len(bases_de_datos), 'CONDICIONPAGO')