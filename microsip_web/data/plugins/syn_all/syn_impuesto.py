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

from ....libs.api.models import Impuesto, ImpuestoTipo
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Impuesto)
def SincronizarImpuesto(sender, **kwargs):
    ''' Para sincronizar impuestos en todas las empreas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        impuesto_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 100, 'IMPUESTO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            
            impuesto_old = first_or_none(Impuesto.objects.using(default_db).filter(pk=impuesto_a_syncronizar.id))

            if impuesto_old:
                impuesto_nombre = impuesto_old.nombre
            else:
                impuesto_nombre = impuesto_a_syncronizar.nombre
     
            impuesto = first_or_none(Impuesto.objects.using(base_de_datos).filter(nombre=impuesto_nombre))

            if impuesto:
                tipo_impuesto = first_or_none(ImpuestoTipo.objects.using(base_de_datos).filter(nombre=impuesto_old.tipoImpuesto.nombre))

                if tipo_impuesto:
                    impuesto.porcentaje = impuesto_old.porcentaje
                    impuesto.nombre= impuesto_old.nombre
                    impuesto.tipoImpuesto = tipo_impuesto
                    impuesto.tipo_iva = impuesto_old.tipo_iva
                    impuesto.es_predet= impuesto_old.es_predet
                    impuesto.save(using=base_de_datos)
            else:
                tipo_impuesto = first_or_none(ImpuestoTipo.objects.using(base_de_datos).filter(nombre=impuesto_old.tipoImpuesto.nombre))
                if tipo_impuesto:
                    Impuesto.objects.using(base_de_datos).create(
                            id=-1,
                            nombre= impuesto_old.nombre,
                            tipoImpuesto = tipo_impuesto,
                            tipo_iva = impuesto_old.tipo_iva,
                            porcentaje = impuesto_old.porcentaje
                        )
        set_indices(indice_final, len(bases_de_datos), 'IMPUESTO')