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

from ....libs.api.models import Articulo, LineaArticulos, ArticuloClave, ArticuloClaveRol, ImpuestosArticulo, Impuesto

from microsip_web.settings.common import MICROSIP_DATABASES
from microsip_web.libs.custom_db.main import first_or_none
from .syn_libs import get_indices, set_indices, default_db

@receiver(pre_save, sender=Articulo)
def SincronizarArticulo(sender, **kwargs):
    ''' Para sincronizar articulos en todas las empreas registradas. '''
    if kwargs.get('using') == default_db:
        bases_de_datos = MICROSIP_DATABASES.keys()
        bases_de_datos.remove(kwargs.get('using'))
        
        articulo_a_syncronizar =  kwargs.get('instance')

        indice, indice_final = get_indices(len(bases_de_datos), 40, 'ARTICULO')
        for base_de_datos in bases_de_datos[indice:indice_final]:
            try:
                articulo_nombre = Articulo.objects.using(default_db).get(pk=articulo_a_syncronizar.id).nombre
            except ObjectDoesNotExist: 
                articulo_nombre = articulo_a_syncronizar.nombre
                
            articulo = first_or_none(Articulo.objects.using(base_de_datos).filter(nombre=articulo_nombre))
            if articulo:
                articulo.nombre = articulo_a_syncronizar.nombre
                articulo.es_almacenable = articulo_a_syncronizar.es_almacenable
                articulo.estatus = articulo_a_syncronizar.estatus
                articulo.seguimiento = articulo_a_syncronizar.seguimiento
                articulo.cuenta_ventas = articulo_a_syncronizar.cuenta_ventas

                linea = LineaArticulos.objects.using(base_de_datos).get(nombre=articulo_a_syncronizar.linea.nombre)
                articulo.linea = linea

                articulo.nota_ventas = articulo_a_syncronizar.nota_ventas
                articulo.unidad_venta = articulo_a_syncronizar.unidad_venta
                articulo.unidad_compra = articulo_a_syncronizar.unidad_compra
                articulo.costo_ultima_compra = articulo_a_syncronizar.costo_ultima_compra
                articulo.usuario_ult_modif = articulo_a_syncronizar.usuario_ult_modif
                articulo.save(using=base_de_datos)
            else:
                linea = LineaArticulos.objects.using(base_de_datos).get(nombre=articulo_a_syncronizar.linea.nombre)
                
                Articulo.objects.using(base_de_datos).create(
                        nombre = articulo_a_syncronizar.nombre,
                        es_almacenable = articulo_a_syncronizar.es_almacenable,
                        estatus = articulo_a_syncronizar.estatus,
                        seguimiento = articulo_a_syncronizar.seguimiento,
                        cuenta_ventas = articulo_a_syncronizar.cuenta_ventas,
                        linea = linea,
                        nota_ventas = articulo_a_syncronizar.nota_ventas,
                        unidad_venta = articulo_a_syncronizar.unidad_venta,
                        unidad_compra = articulo_a_syncronizar.unidad_compra,
                        costo_ultima_compra = articulo_a_syncronizar.costo_ultima_compra,
                        usuario_ult_modif = articulo_a_syncronizar.usuario_ult_modif,
                    )

            SincronizarDependencias(using=base_de_datos, articulo_nombre=articulo_nombre)

        set_indices(indice_final, len(bases_de_datos), 'ARTICULO')

def SincronizarDependencias(**kwargs):
    ''' Para sincronizar primer plazo de condiciones de pago en todas las empreas registradas. '''
    using =  kwargs.get('using')
    articulo_nombre= kwargs.get('articulo_nombre')
    #DATOS FUENTE
    fuente_articulo = Articulo.objects.using(default_db).get(nombre=articulo_nombre)
    fuente_articulo_clave = first_or_none(ArticuloClave.objects.using(default_db).filter(articulo=fuente_articulo, rol__es_ppal='S'))
    fuente_impuesto_articulo = first_or_none(ImpuestosArticulo.objects.using(default_db).filter(articulo=fuente_articulo))

    #DATOS ORIGEN
    articulo = Articulo.objects.using(using).get(nombre=articulo_nombre)

    ####################################
    #  Actualiza la primer clave
    ####################################
    articulo_clave = first_or_none(ArticuloClave.objects.using(using).filter(articulo=articulo, rol__es_ppal='S'))
    rol_principal = ArticuloClaveRol.objects.using(using).get(es_ppal='S')
    
    if articulo_clave:
        articulo_clave.clave = fuente_articulo_clave.clave
        articulo_clave.articulo = articulo
        articulo_clave.rol = rol_principal
        articulo_clave.save(using=using)
    else:
        ArticuloClave.objects.using(using).create(
                clave = fuente_articulo_clave.clave,
                articulo = articulo,
                rol = rol_principal,
            )

    ####################################
    #  Actualiza el primer impuesto
    ####################################    
    impuesto_articulo = first_or_none(ImpuestosArticulo.objects.using(using).filter(articulo=articulo))
    impuesto = Impuesto.objects.using(using).get(nombre=fuente_impuesto_articulo.impuesto.nombre)

    if impuesto_articulo:
        impuesto_articulo.impuesto = impuesto
        impuesto_articulo.save(using=using)
    else:
        ImpuestosArticulo.objects.using(using).create(
                    articulo = articulo,
                    impuesto = impuesto,
                )