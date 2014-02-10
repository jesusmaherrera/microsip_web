#encoding:utf-8
'''
    Plugin para:
        Para sincronizar todas las ciudades de las bases de datos
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver

from ....libs.api.models import Ciudad, Estado, Pais
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Ciudad)
def Sincronizarciudad(sender, **kwargs):
    ''' Para sincronizar ciudad en todas las empreas. '''
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        ciudad_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 100, 'CIUDAD')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            ciudad_old = first_or_none(Ciudad.objects.using(default_db).filter(pk=ciudad_a_syncronizar.id))
            if ciudad_old:
                ciudad_nombre = ciudad_old.nombre
            else:
                ciudad_nombre = ciudad_a_syncronizar.nombre

            ciudad = first_or_none(Ciudad.objects.using(base_de_datos).filter(nombre=ciudad_nombre))

            old_estado = ciudad_a_syncronizar.estado
            old_pais = old_estado.pais

            pais, pais_creado = Pais.objects.using(base_de_datos).get_or_create(
                    nombre= old_estado.pais.nombre,
                    defaults={
                        'nombre': old_pais.nombre,
                        'es_predet': old_pais.es_predet, 
                        'nombre_abreviado': old_pais.nombre_abreviado,
                    }
                )

            estado, estado_creado = Estado.objects.using(base_de_datos).get_or_create(
                    nombre=ciudad_a_syncronizar.estado.nombre, 
                    defaults={
                        'es_predet': old_estado.es_predet,
                        'nombre_abreviado':old_estado.nombre_abreviado,
                        'pais': pais,
                    }
                )

            if ciudad:
                ciudad.nombre= ciudad_a_syncronizar.nombre
                ciudad.es_predet= ciudad_a_syncronizar.es_predet
                ciudad.estado = estado
                ciudad.save(using=base_de_datos)
            else:
                Ciudad.objects.using(base_de_datos).create(
                            id=-1,
                            nombre= ciudad_a_syncronizar.nombre,
                            es_predet= ciudad_a_syncronizar.es_predet,
                            estado = estado
                        )
        set_indices(indice_final, len(bases_de_datos), 'CIUDAD')