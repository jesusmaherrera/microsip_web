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
from django.db import router
from ....libs.api.models import Articulos, ClavesArticulos, RolesClavesArticulos, articulo_clave_save_signal
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db




@receiver(post_save, sender=ClavesArticulos)
def SincronizarArticuloImpuesto(sender, **kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''
    instance  = kwargs.get('instance')

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        articulo_clave_a_syncronizar =  instance
        articulo_nombre = articulo_clave_a_syncronizar.articulo.nombre
        indice, indice_final = get_indices(len(bases_de_datos), 40, 'ARTICULO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            articulo = Articulos.objects.using(base_de_datos).get(nombre=articulo_nombre)
                
            clave_principal = first_or_none(ClavesArticulos.objects.using(base_de_datos).filter(articulo=articulo, rol__es_ppal='S'))


            rol_principal = RolesClavesArticulos.objects.using(base_de_datos).get(es_ppal='S')

            if clave_principal:
                clave_principal.clave = articulo_clave_a_syncronizar.clave
                clave_principal.articulo = articulo
                clave_principal.rol = rol_principal
                clave_principal.save(using=base_de_datos)
            else:
                ClavesArticulos.objects.using(base_de_datos).create(
                        clave = articulo_clave_a_syncronizar.clave,
                        articulo = articulo,
                        rol = rol_principal,
                    )
                
        # set_indices(indice_final, len(bases_de_datos), 'ARTICULO')

@receiver(articulo_clave_save_signal)
def my_callback(sender,*args, **kwargs):
    SincronizarArticuloImpuesto(sender, instance = sender, *args, **kwargs)