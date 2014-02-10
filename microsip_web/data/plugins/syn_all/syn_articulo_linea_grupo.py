#encoding:utf-8
'''
    Plugin para:
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver

from ....libs.api.models import GrupoLineas
from microsip_web.libs.tools import split_seq
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=GrupoLineas)
def SincronizarArticuloGrupo(sender, **kwargs):
    ''' Para sincronizar ciudad en todas las empreas. '''
    
    
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        articulo_grupo_a_syncronizar =  kwargs.get('instance')
        
        indice, indice_final = get_indices(len(bases_de_datos), 100, 'GRUPO')
        for base_de_datos in bases_de_datos[indice:indice_final]:

            articulo_grupo_old = first_or_none(GrupoLineas.objects.using(default_db).filter(pk=articulo_grupo_a_syncronizar.id))
            if articulo_grupo_old:
                articulo_grupo_nombre = articulo_grupo_old.nombre
            else:
                articulo_grupo_nombre = articulo_grupo_a_syncronizar.nombre

            articulo_grupo = first_or_none(GrupoLineas.objects.using(base_de_datos).filter(nombre=articulo_grupo_nombre))
            if articulo_grupo:
                articulo_grupo.nombre= articulo_grupo_a_syncronizar.nombre
                articulo_grupo.cuenta_ventas= articulo_grupo_a_syncronizar.cuenta_ventas
                articulo_grupo.save(using=base_de_datos)
            else:
                GrupoLineas.objects.using(base_de_datos).create(
                            nombre= articulo_grupo_a_syncronizar.nombre,
                            cuenta_ventas = articulo_grupo_a_syncronizar.cuenta_ventas,
                        )

        set_indices(indice_final, len(bases_de_datos), 'GRUPO')