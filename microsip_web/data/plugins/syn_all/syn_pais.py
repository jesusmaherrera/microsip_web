#encoding:utf-8
'''
    Plugin para:
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver

from ....libs.api.models import Pais
from microsip_web.libs.tools import split_seq
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Pais)
def SincronizarPais(sender, **kwargs):
    ''' Para sincronizar ciudad en todas las empreas. '''
    
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        pais_a_syncronizar =  kwargs.get('instance')
        indice, indice_final = get_indices(len(bases_de_datos), 100, 'PAIS')
        for base_de_datos in bases_de_datos[indice:indice_final]:

            pais_old = first_or_none(Pais.objects.using(default_db).filter(pk=pais_a_syncronizar.id))

            if pais_old:
                pais_nombre = pais_old.nombre
            else:
                pais_nombre = pais_a_syncronizar.nombre

            pais = first_or_none(Pais.objects.using(base_de_datos).filter(nombre=pais_nombre))
            
            if pais:
                pais.nombre= pais_a_syncronizar.nombre
                pais.es_predet= pais_a_syncronizar.es_predet
                pais.nombre_abreviado= pais_a_syncronizar.nombre_abreviado
                
                pais.save(using=base_de_datos)
            else:
                Pais.objects.using(base_de_datos).create(
                            id=-1,
                            nombre= pais_a_syncronizar.nombre,
                            es_predet = pais_a_syncronizar.es_predet,
                            nombre_abreviado = pais_a_syncronizar.nombre_abreviado
                        )

        set_indices(indice_final, len(bases_de_datos), 'PAIS')