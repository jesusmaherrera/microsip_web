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

from ....libs.api.models import Cliente, DirCliente, Ciudad, Estado, Pais
from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(post_save, sender=DirCliente)
def SincronizarClienteDireccion(sender, **kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''

    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        direccion_a_syncronizar =  kwargs.get('instance')
        cliente_nombre = direccion_a_syncronizar.cliente.nombre
        
        indice, indice_final = get_indices(len(bases_de_datos), 40, 'CLIENTE')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            cliente = Cliente.objects.using(base_de_datos).get(nombre=cliente_nombre)
                
            direccion = first_or_none(DirCliente.objects.using(base_de_datos).filter(cliente= cliente))
            
            if direccion:
                direccion.rfc_curp = direccion_a_syncronizar.rfc_curp
                ciudad = Ciudad.objects.using(base_de_datos).get(nombre=direccion_a_syncronizar.ciudad.nombre)
                
                direccion.ciudad = ciudad
                direccion.colonia = direccion_a_syncronizar.colonia
                direccion.nombre_consignatario = direccion_a_syncronizar.nombre_consignatario
                direccion.calle = direccion_a_syncronizar.calle
                direccion.es_ppal = direccion_a_syncronizar.es_ppal
                direccion.poblacion = direccion_a_syncronizar.poblacion
                direccion.referencia = direccion_a_syncronizar.referencia

                direccion.codigo_postal = direccion_a_syncronizar.codigo_postal
                direccion.calle_nombre = direccion_a_syncronizar.calle_nombre
                direccion.numero_exterior = direccion_a_syncronizar.numero_exterior
                direccion.numero_interior = direccion_a_syncronizar.numero_interior
                direccion.email = direccion_a_syncronizar.email

                direccion.save(using=base_de_datos)
            else:
                ciudad_original_nombre = direccion_a_syncronizar.ciudad.nombre
                estado_original_nombre = direccion_a_syncronizar.estado.nombre
                pais_original_nombre = direccion_a_syncronizar.pais.nombre

                ciudad = Ciudad.objects.using(base_de_datos).get(nombre=ciudad_original_nombre)
                estado = Estado.objects.using(base_de_datos).get(nombre=estado_original_nombre)
                pais = Pais.objects.using(base_de_datos).get(nombre=pais_original_nombre)

                DirCliente.objects.using(base_de_datos).create(
                            cliente = cliente,
                            rfc_curp = direccion_a_syncronizar.rfc_curp,
                            ciudad = ciudad,
                            estado = estado,
                            pais = pais,
                            colonia = direccion_a_syncronizar.colonia,
                            nombre_consignatario = direccion_a_syncronizar.nombre_consignatario,
                            calle = direccion_a_syncronizar.calle,
                            es_ppal = direccion_a_syncronizar.es_ppal,
                            poblacion = direccion_a_syncronizar.poblacion,
                            referencia = direccion_a_syncronizar.referencia,
                            codigo_postal = direccion_a_syncronizar.codigo_postal,
                            calle_nombre = direccion_a_syncronizar.calle_nombre,
                            numero_exterior = direccion_a_syncronizar.numero_exterior,
                            numero_interior = direccion_a_syncronizar.numero_interior,
                            email = direccion_a_syncronizar.email
                        )

        #set_indices(indice_final, len(bases_de_datos), 'CLIENTE')