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

from ....libs.api.models import Cliente, CondicionPago
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Cliente)
def SincronizarCliente(sender, **kwargs):
    ''' Para sincronizar clientes en todas las empreas registradas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        cliente_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 40, 'CLIENTE')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            try:
                cliente_nombre = Cliente.objects.using(default_db).get(pk=cliente_a_syncronizar.id).nombre
            except ObjectDoesNotExist: 
                cliente_nombre = cliente_a_syncronizar.nombre
                
            cliente = first_or_none(Cliente.objects.using(base_de_datos).filter(nombre=cliente_nombre))
            if cliente:
                cliente.nombre = cliente_a_syncronizar.nombre
                
                condicion_de_pago = CondicionPago.objects.using(base_de_datos).get(nombre=cliente_a_syncronizar.condicion_de_pago.nombre)
                cliente.condicion_de_pago = condicion_de_pago

                cliente.moneda = cliente_a_syncronizar.moneda
                cliente.cobrar_impuestos = cliente_a_syncronizar.cobrar_impuestos
                cliente.generar_interereses = cliente_a_syncronizar.generar_interereses
                cliente.emir_estado_cuenta = cliente_a_syncronizar.emir_estado_cuenta
                

                cliente.save(using=base_de_datos)
            else:
                condicion_de_pago = CondicionPago.objects.using(base_de_datos).get(nombre=cliente_a_syncronizar.condicion_de_pago.nombre)
                
                Cliente.objects.using(base_de_datos).create(
                        nombre = cliente_a_syncronizar.nombre,
                        condicion_de_pago = condicion_de_pago,
                        moneda = cliente_a_syncronizar.moneda,
                        cobrar_impuestos = cliente_a_syncronizar.cobrar_impuestos,
                        generar_interereses = cliente_a_syncronizar.generar_interereses,
                        emir_estado_cuenta = cliente_a_syncronizar.emir_estado_cuenta,
                    )
        set_indices(indice_final, len(bases_de_datos), 'CLIENTE')