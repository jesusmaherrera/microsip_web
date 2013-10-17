 #encoding:utf-8
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
import json
import datetime, time
from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo
from microsip_web.libs.tools import split_seq
from django.db import connections
from microsip_web.libs.custom_db.main import get_conecctionname

@dajaxice_register( method = 'GET' )
def get_detallesArticuloenInventario( request, detalle_invfis_id ):
    """ Obtiene detalle de movimientos (con fecha y hora) en inventario de un detalle de inventario.  """

    detalle_doc = DoctosInvfisDet.objects.get( pk = detalle_invfis_id )
    detalle = detalle_doc.detalle_modificacionestime
    return simplejson.dumps( { 'detalle' : detalle, } ) 

@dajaxice_register( method = 'GET' )
def sincronizar_inventario( request, inventariofisico_id ):
    """ Sincronoza movimientos en inventario con datos introducidos directamente en inventario fisico.  """

    basedatos_activa = request.session[ 'selected_database' ]
    if basedatos_activa == '':
        return HttpResponseRedirect( '/select_db/' )
    else:
        conexion_activa_id = request.session[ 'conexion_activa' ]
    conexion_name = "%02d-%s"%( conexion_activa_id, basedatos_activa )
    
    #Variables iniciales
    articulos_modificados = 0
    inventario_fisico = DoctosInvfis.objects.get( pk = inventariofisico_id )
    fecha_actual_str = datetime.now().strftime( "%m/%d/%Y" )
    fecha_inventario_str = inventario_fisico.fecha.strftime( "%m/%d/%Y" )

    c = connections[ conexion_name ].cursor()
    c.execute("""
        SELECT B.ARTICULO_ID, B.ENTRADAS_UNID, B.SALIDAS_UNID FROM articulos A
        LEFT JOIN orsp_in_aux_art( articulo_id, '%s', '%s','%s','S','N') B
        ON A.articulo_id = B.articulo_id
        """% ( inventario_fisico.almacen.nombre, fecha_inventario_str, fecha_actual_str ) )
    unidades_rows = c.fetchall()
    c.close() 
    
    for unidades_row in unidades_rows:
        articulo = Articulos.objects.get( pk = unidades_row[0] )
        entradas = Decimal(unidades_row[1])
        salidas = Decimal(unidades_row[2])
        diferencia_unidades = entradas - salidas
        try:
            detalle = DoctosInvfisDet.objects.get( articulo = articulo, docto_invfis = inventariofisico_id )
        except ObjectDoesNotExist:
            pass
            # articulos_claves = ClavesArticulos.objects.filter( articulo = articulo )
                        
            # if articulos_claves.count() < 1:
            #     articulo_clave = ''
            # else:
            #     articulo_clave = articulos_claves[0].clave

            # if articulo.seguimiento == 'S':
            #     c = connections[ conexion_name ].cursor()
            #     c.execute("""
            #         SELECT B.art_discreto_id, B.existencia FROM LISTA_ARTS_DISCRETOS('S', 'E', %s, NULL, NULL, %s, NULL) B
            #         """% ( inventario_fisico.almacen.ALMACEN_ID, articulo.id ) )
            #     series = c.fetchall()
            #     c.close()

            #     if len(series) > 0:
            #         detalle = DoctosInvfisDet(
            #             id = next_id( 'ID_DOCTOS', conexion_name ),
            #             docto_invfis= inventario_fisico,
            #             clave= articulo_clave,
            #             articulo = articulo,
            #             unidades = len( series ),
            #             usuario_ult_modif = request.user.username,
            #             unidades_syn = len(series),
            #             )

            #         detalle.save(force_insert=True)
            #         articulos_modificados += 1

            #         for articulo_discreto in series:
            #             DesgloseEnDiscretosInvfis.objects.create( id = -1, docto_invfis_det = detalle, art_discreto = ArticulosDiscretos.objects.get( pk = articulo_discreto[0] ), unidades = articulo_discreto[1] )
                        

            # if articulo.seguimiento == 'N':
            #     if diferencia_unidades != 0:
            #         detalle = DoctosInvfisDet(
            #             id = next_id( 'ID_DOCTOS', conexion_name ),
            #             docto_invfis = inventario_fisico,
            #             clave = articulo_clave,
            #             articulo = articulo,
            #             unidades = unidades_row[1],
            #             usuario_ult_modif = request.user.username,
            #             unidades_syn = unidades_row[1],
            #             )

            #         detalle.save( force_insert = True )
            #         articulos_modificados += 1
        else:
            if detalle.articulo.seguimiento == 'S':
                c = connections[conexion_name].cursor()
                c.execute("""
                    SELECT B.art_discreto_id, B.existencia FROM LISTA_ARTS_DISCRETOS('S', 'E', %s, NULL, NULL, %s, NULL) B
                    WHERE B.art_discreto_id NOT IN 
                        (SELECT A.art_discreto_id FROM DESGLOSE_EN_DISCRETOS_INVFIS A where A.docto_invfis_det_id = %s)
                    """% ( inventario_fisico.almacen.ALMACEN_ID, detalle.articulo.id, detalle.id ) )
                series = c.fetchall()
                for articulo_discreto in series:
                    DesgloseEnDiscretosInvfis.objects.create( id = -1, docto_invfis_det = detalle, art_discreto = ArticulosDiscretos.objects.get( pk = articulo_discreto[0] ), unidades = articulo_discreto[1] )
                    articulos_modificados += 1
                c.close()

                
                desgloses = DesgloseEnDiscretosInvfis.objects.filter( docto_invfis_det = detalle ) 
                desgloses_inv = DesgloseEnDiscretosInvfis.objects.filter( sic_nuevo = 'S' ).filter( docto_invfis_det = detalle ) 
                articulos_dis_invfis = desgloses.values_list('art_discreto__id', flat=True)
                
                articulos_a_eliminar = ExistDiscreto.objects.filter( articulo_discreto__id__in = articulos_dis_invfis, existencia = 0 ).values_list( 'articulo_discreto__id', flat = True )
                DesgloseEnDiscretosInvfis.objects.exclude( sic_nuevo = 'S' ).filter( docto_invfis_det = detalle, art_discreto_id__in =  articulos_a_eliminar ).delete()

                detalle.unidades = len( desgloses )
                detalle.unidades_syn = len( desgloses ) - len( desgloses_inv )
                detalle.save()

            if detalle.articulo.seguimiento == 'N':
                if diferencia_unidades != detalle.unidades_syn: 
                    detalle.unidades_syn = detalle.unidades_syn
                    detalle.unidades_margen = detalle.unidades_margen - detalle.unidades_syn

                    if detalle.unidades_margen >= 1000000:
                        detalle.unidades = detalle.unidades_margen - 1000000
                        detalle.unidades_syn = detalle.unidades_syn
                        detalle.save()
                        articulos_modificados += 1

    return simplejson.dumps( { 'articulos_count' : articulos_modificados } )


@dajaxice_register( method = 'GET' )
def get_existencias_articulo_view( request, articulo_id, almacen = '' ):
    connection_name = get_conecctionname( request.session )
    if connection_name == '':
        return HttpResponseRedirect( '/select_db/' )
    articulo = Articulos.objects.get( pk = articulo_id )
    entradas, salidas, existencias, inv_fin = get_existencias_articulo(
        articulo_id = articulo_id , 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "%m/01/%Y" ),
        almacen = almacen, )

    return simplejson.dumps( { 'existencias' : int( inv_fin ), 'costo_ultima_compra' : str(articulo.costo_ultima_compra) } )

@dajaxice_register( method = 'GET' )
def add_aticulosinventario( request, inventario_id, articulo_id, unidades, ubicacion ):
    """ Agrega articulo a inventario.  """

    basedatos_activa = request.session[ 'selected_database' ]
    if basedatos_activa == '':
        return HttpResponseRedirect( '/select_db/' )
    else:
        conexion_activa_id = request.session[ 'conexion_activa' ]

    conexion_name = "%02d-%s"%( conexion_activa_id, basedatos_activa )

    message = ''
    msg_series=''
    error = 0
    inicio_form = False
    movimiento = ''
    
    articulo_clave = ClavesArticulos.objects.filter( articulo__id = articulo_id ).first()
    
    try:
        doc = DoctosInvfisDet.objects.get( docto_invfis__id = inventario_id, articulo__id = articulo_id )
        str_unidades = unidades
        unidades = Decimal( unidades )
        doc_unidades = doc.unidades
        
        unidades = doc.unidades + unidades
        if unidades < 0:
            unidades = 0
        movimiento = 'actualizar'
    except:
        if unidades >= 0:
            movimiento = 'crear'

    if movimiento == 'crear':
        DoctosInvfisDet.objects.create(
            id = next_id( 'ID_DOCTOS', conexion_name ),
            docto_invfis = DoctosInvfis.objects.get( pk = inventario_id ),
            clave = articulo_clave,
            unidades = unidades, 
            articulo = Articulos.objects.get( pk = articulo_id ),
            usuario_ult_modif = request.user.username,
            detalle_modificaciones = '[%s/%s=%s], '%( request.user.username, ubicacion, unidades ),
            )
    elif movimiento == 'actualizar':
        doc.fechahora_ult_modif = datetime.now()
        doc.unidades = unidades
        doc.clave = articulo_clave
        doc.usuario_ult_modif = request.user.username
        if doc.detalle_modificaciones == None:
            doc.detalle_modificaciones = ''
        if doc.detalle_modificacionestime == None:
            doc.detalle_modificacionestime = ''

        tamano_detalles = len( doc.detalle_modificaciones + '[%s/%s=%s],'%( request.user.username, ubicacion, str_unidades ) )
    
        if  tamano_detalles  < 400:
            doc.detalle_modificaciones += '[%s/%s=%s],'%( request.user.username, ubicacion, str_unidades )
        else:
            message = "El numero de caracteres para detalles del articulo fue excedido"

        doc.detalle_modificacionestime += '[%s/%s=%s](%s),'%( request.user.username, ubicacion, str_unidades, datetime.now().strftime( "%d-%m-%Y %H:%M" ) )

        doc.save()

    return simplejson.dumps( { 'message' : 'exito' } )

@dajaxice_register( method = 'GET' )
def get_articulosen_inventario( request, inventario_id, articulo_id ):
    """ Para obtener las unidades en inventario de un determinado articulo. """

    detalle_modificaciones = ''
    articulo_seguimiento = ''
    try:
        doc = DoctosInvfisDet.objects.get( docto_invfis__id = inventario_id, articulo_id = articulo_id )
        unidades = doc.unidades
        detalle_modificaciones = doc.detalle_modificaciones
        articulo_seguimiento = doc.articulo.seguimiento
    except ObjectDoesNotExist:
        unidades = 0
        articulo_seguimiento = Articulos.objects.get( pk = articulo_id ).seguimiento
    
    return simplejson.dumps( { 'unidades' : str(unidades), 'detalle_modificaciones' : detalle_modificaciones, 'articulo_seguimiento' : articulo_seguimiento, } )

@dajaxice_register( method = 'GET' )
def get_articulo_by_clave( request, clave ):
    """ para obtener datos principales de un articulo por clave.  """

    opciones = {}
    try:
        clave_articulo = ClavesArticulos.objects.get( clave = clave )
        articulo_id = clave_articulo.articulo.id
        articulo_nombre = clave_articulo.articulo.nombre
        articulo_seguimiento = clave_articulo.articulo.seguimiento
    except ObjectDoesNotExist:
        claves = ClavesArticulos.objects.filter( clave__contains = clave )
        for c in claves:
            opciones[ str( c.clave ) ] = c.articulo.nombre

        articulo_id = 0
        articulo_nombre = ''
        articulo_seguimiento = ''
    
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    datos = { "articulo_id" : articulo_id, "articulo_nombre" : articulo_nombre, "articulo_seguimiento" : articulo_seguimiento, "opciones" : opciones }
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def add_articulos_nocontabilizados_porlinea( request, inventario_id = None, linea_id = None ):
    """ Agrega articulos almacenables de la linea uindicada faltantes en inventario en ceros.  """

    inventario_fisico = DoctosInvfis.objects.get( pk = inventario_id )
    linea = LineaArticulos.objects.get( pk = linea_id )
    articulos_enInventario = DoctosInvfisDet.objects.filter( docto_invfis = inventario_fisico ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True )
    all_articulos_enceros = Articulos.objects.filter( es_almacenable = 'S', linea = linea ).exclude( pk__in = articulos_enInventario ).order_by( '-id' ).values_list( 'id', flat = True )
    
    articulos_enceros = all_articulos_enceros[0:9000]

    articulos_enceros_list = split_seq( articulos_enceros, 2000 )
    articulos_agregados = 0

    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter( articulo__id = articulo_id )
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario =DoctosInvfisDet(
                id=-1,
                docto_invfis= inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get( pk = articulo_id ),
                unidades = 0 )


            detalles_en_ceros.append( detalle_inventario )
        
        articulos_agregados = articulos_agregados + len( detalles_en_ceros )
        DoctosInvfisDet.objects.bulk_create( detalles_en_ceros )

    articulos_pendientes = all_articulos_enceros.count() -  articulos_agregados
    return simplejson.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, } )

@dajaxice_register( method = 'GET' )
def add_articulos_nocontabilizados( request, inventario_id = None ):
    """ Agrega articulos almacenables faltantes en inventario en ceros.  """

    inventario_fisico = DoctosInvfis.objects.get( pk = inventario_id )
    articulos_enInventario = DoctosInvfisDet.objects.filter( docto_invfis = inventario_fisico ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True )
    all_articulos_enceros = Articulos.objects.filter( es_almacenable = 'S' ).exclude( pk__in = articulos_enInventario ).order_by( '-id' ).values_list( 'id', flat = True )
    articulos_enceros = all_articulos_enceros[0:9000]
    articulos_enceros_list = split_seq( articulos_enceros, 2000 )
    articulos_agregados = 0
    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter( articulo__id = articulo_id )
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario = DoctosInvfisDet(
                id =-1,
                docto_invfis = inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get( pk = articulo_id ),
                unidades = 0 )


            detalles_en_ceros.append( detalle_inventario )
    
        articulos_agregados = articulos_agregados + len( detalles_en_ceros )
        DoctosInvfisDet.objects.bulk_create( detalles_en_ceros )

    articulos_pendientes = all_articulos_enceros.count() -  articulos_agregados
    return simplejson.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, } )
