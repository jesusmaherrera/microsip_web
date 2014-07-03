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

from microsip_web.libs.api.models import Cliente, CondicionPago, ClienteDireccion, Ciudad, Estado, Pais
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db
from django.conf import settings

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
            
            SincronizarClienteDireccion(using=base_de_datos, fuente_cliente_nombre=cliente_nombre )

        set_indices(indice_final, len(bases_de_datos), 'CLIENTE')


def SincronizarClienteDireccion(**kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''
    using =  kwargs.get('using')

    #DATOS ORIGEN
    fuente_cliente_nombre = kwargs.get('fuente_cliente_nombre')    
    fuente_cliente = Cliente.objects.using(default_db).get(nombre=fuente_cliente_nombre)
    fuente_direccion = first_or_none(ClienteDireccion.objects.using(default_db).filter(cliente= fuente_cliente))

    #DATOS DESTINO
    cliente = Cliente.objects.using(using).get(nombre=fuente_cliente.nombre)
    direccion = first_or_none(ClienteDireccion.objects.using(using).filter(cliente= cliente))
    
    if direccion:
        direccion.rfc_curp = fuente_direccion.rfc_curp
        ciudad = Ciudad.objects.using(using).get(nombre=fuente_direccion.ciudad.nombre)
        
        direccion.ciudad = ciudad
        direccion.colonia = fuente_direccion.colonia
        direccion.nombre_consignatario = fuente_direccion.nombre_consignatario
        direccion.calle = fuente_direccion.calle
        direccion.es_ppal = fuente_direccion.es_ppal
        if settings.MICROSIP_VERSION >= 2013:
            direccion.poblacion = fuente_direccion.poblacion
        direccion.referencia = fuente_direccion.referencia

        direccion.codigo_postal = fuente_direccion.codigo_postal
        direccion.calle_nombre = fuente_direccion.calle_nombre
        direccion.numero_exterior = fuente_direccion.numero_exterior
        direccion.numero_interior = fuente_direccion.numero_interior
        direccion.email = fuente_direccion.email

        direccion.save(using=using)
    else:
        ciudad_original_nombre = fuente_direccion.ciudad.nombre
        estado_original_nombre = fuente_direccion.estado.nombre
        pais_original_nombre = fuente_direccion.pais.nombre
        
        ciudad = Ciudad.objects.using(using).filter(nombre=ciudad_original_nombre).values_list( 'id', flat = True )[0]
        estado = Estado.objects.using(using).filter(nombre=estado_original_nombre).values_list( 'id', flat = True )[0]
        pais = Pais.objects.using(using).filter(nombre=pais_original_nombre).values_list( 'id', flat = True )[0]
        
        kwargs = {
            'cliente': cliente.id,
            'rfc_curp': fuente_direccion.rfc_curp,
            'ciudad': ciudad,
            'estado': estado,
            'pais': pais,
            'colonia': fuente_direccion.colonia,
            'nombre_consignatario': fuente_direccion.nombre_consignatario,
            'calle': fuente_direccion.calle,
            'es_ppal': fuente_direccion.es_ppal,
            'referencia': fuente_direccion.referencia,
            'codigo_postal': fuente_direccion.codigo_postal,
            'calle_nombre': fuente_direccion.calle_nombre,
            'numero_exterior': fuente_direccion.numero_exterior,
            'numero_interior': fuente_direccion.numero_interior,
            'email': fuente_direccion.email,
            'using':using,
        }
        
        if settings.MICROSIP_VERSION >= 2013:
            kwargs['poblacion']= fuente_direccion.poblacion
        
        ClienteDireccion.objects.create_simple(**kwargs)