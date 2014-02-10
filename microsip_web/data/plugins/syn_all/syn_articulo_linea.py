#encoding:utf-8
'''
    Plugin para:
        
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''

from django.db.models.signals import pre_save
from django.dispatch import receiver

from ....libs.api.models import LineaArticulos, GrupoLineas
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=LineaArticulos)
def SincronizarEstado(sender, **kwargs):
    ''' Para sincronizar LineaArticulos en todas las empreas. '''
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        articulo_linea_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 100, 'LINEA')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            articulo_linea_old = first_or_none(LineaArticulos.objects.using(default_db).filter(pk=articulo_linea_a_syncronizar.id))
            if articulo_linea_old:
                articulo_linea_nombre = articulo_linea_old.nombre
            else:
                articulo_linea_nombre = articulo_linea_a_syncronizar.nombre

            articulo_linea = first_or_none(LineaArticulos.objects.using(base_de_datos).filter(nombre=articulo_linea_nombre))

            articulo_grupo = first_or_none(GrupoLineas.objects.using(base_de_datos).filter(nombre=articulo_linea_a_syncronizar.grupo.nombre))

            if not articulo_grupo:
                articulo_grupo_old = articulo_linea_a_syncronizar.grupo

                articulo_grupo = GrupoLineas.objects.using(base_de_datos).create(
                        nombre = articulo_grupo_old.nombre,
                        cuenta_ventas= articulo_grupo_old.cuenta_ventas,
                    )

            if articulo_linea:
                articulo_linea.nombre= articulo_linea_a_syncronizar.nombre
                articulo_linea.cuenta_ventas = articulo_linea_a_syncronizar.cuenta_ventas
                articulo_linea.grupo = articulo_grupo
                articulo_linea.save(using=base_de_datos)
            else:
                LineaArticulos.objects.using(base_de_datos).create(
                            nombre= articulo_linea_a_syncronizar.nombre,
                            grupo = articulo_grupo,
                        )

        set_indices(indice_final, len(bases_de_datos), 'LINEA')