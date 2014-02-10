#encoding:utf-8
'''
    Plugin para:
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver

from ....libs.api.models import Estado, Pais
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Estado)
def SincronizarEstado(sender, **kwargs):
    ''' Para sincronizar estado en todas las empreas. '''
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        estado_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 100, 'ESTADO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            estado_old = first_or_none(Estado.objects.using(default_db).filter(pk=estado_a_syncronizar.id))
            if estado_old:
                estado_nombre = estado_old.nombre
            else:
                estado_nombre = estado_a_syncronizar.nombre

            estado = first_or_none(Estado.objects.using(base_de_datos).filter(nombre=estado_nombre))

            pais = first_or_none(Pais.objects.using(base_de_datos).filter(nombre=estado_a_syncronizar.pais.nombre))

            if not pais:
                old_pais = estado_a_syncronizar.pais

                pais = Pais.objects.using(base_de_datos).create(
                        nombre = old_pais.nombre,
                        es_predet = old_pais.es_predet,
                        nombre_abreviado = old_pais.nombre_abreviado
                    )

            if estado:
                estado.nombre= estado_a_syncronizar.nombre
                estado.es_predet= estado_a_syncronizar.es_predet
                estado.nombre_abreviado= estado_a_syncronizar.nombre_abreviado
                estado.pais = pais
                estado.save(using=base_de_datos)
            else:
                Estado.objects.using(base_de_datos).create(
                            id=-1,
                            nombre= estado_a_syncronizar.nombre,
                            nombre_abreviado = estado_a_syncronizar.nombre_abreviado,
                            es_predet= estado_a_syncronizar.es_predet,
                            pais = pais
                        )
        set_indices(indice_final, len(bases_de_datos), 'ESTADO')