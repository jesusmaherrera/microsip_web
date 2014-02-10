#encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
#Modelos 
from microsip_web.apps.inventarios.models import *
from microsip_web.libs.custom_db.main import get_existencias_articulo

def ajustar_existencias( **kwargs ):
    ''' Para ajustar un articulo a las unidades indicadas sin importar su existencia actual '''
    #Paramentros
    articulo_id = kwargs.get( 'articulo_id', None )
    ajustar_a = kwargs.get( 'ajustar_a', None )
    almacen = kwargs.get( 'almacen', None )
    connection_name = kwargs.get( 'connection_name', None )

    inv_fin = get_existencias_articulo(
        articulo_id = articulo_id, 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
        almacen = almacen, 
        )

    unidades_a_insertar = -inv_fin + ajustar_a
    return unidades_a_insertar

def ajustes_get_or_create( almacen_id = None, username = '' ):
    ''' Funcion obtener o crear documentos de entrada y salida para trabajar ccon inventario por ajustes'''

    fecha_actual = datetime.now()
    almacen = Almacenes.objects.get( pk = almacen_id )
    conecpto_ajuste_salida = ConceptosIn.objects.get( pk = 38 )
    conecpto_ajuste_entrada = ConceptosIn.objects.get( pk = 27 )
    folio = '' 

    #salida
    try:
        salida = DoctosIn.objects.get( descripcion = 'ES INVENTARIO', cancelado= 'N', concepto = 38, almacen = almacen,  fecha =  fecha_actual )
    except ObjectDoesNotExist:

        salida = DoctosIn(
            almacen =  almacen,
            concepto = conecpto_ajuste_salida,
            naturaleza_concepto = 'S',
            fecha = fecha_actual,
            sistema_origen = 'IN',
            usuario_creador = username,
            descripcion = 'ES INVENTARIO',
             )
        salida.save()

    #salida
    try:
        entrada = DoctosIn.objects.get( descripcion = 'ES INVENTARIO', cancelado= 'N', concepto = 27, almacen = almacen, fecha = fecha_actual )
    except ObjectDoesNotExist:

        entrada = DoctosIn(
            almacen =  almacen,
            concepto = conecpto_ajuste_entrada,
            naturaleza_concepto = 'E',
            fecha = fecha_actual,
            sistema_origen = 'IN',
            usuario_creador = username,
            descripcion = 'ES INVENTARIO',
             )

        entrada.save()

    return entrada, salida