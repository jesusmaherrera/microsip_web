 #encoding:utf-8
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core import management
import json
import datetime, time
from django.db.models import Q
from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none
from microsip_web.libs.tools import split_seq
from django.db import connections, transaction
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

def add_existenciasarticulo_byajustes( **kwargs ):
    """ Para agregar existencia a un articulo por ajuste 
        En caso de que el articulo no tenga costo indicado [se le aplica el de la ultima compra]
    """

    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    articulo_id = kwargs.get( 'articulo_id', None )
    articulo = Articulos.objects.get( pk = articulo_id )

    entrada_id = kwargs.get( 'entrada_id', None )
    entrada = DoctosIn.objects.get( pk = entrada_id )
    almacen = entrada.almacen

    salida_id = kwargs.get( 'salida_id', None )
    salida = DoctosIn.objects.get( pk = salida_id )

    request_session = kwargs.get( 'request_session', 0 )
    request_user = kwargs.get( 'request_user', 0 )
    connection_name = get_conecctionname( request_session )
    
    detalle_unidades = kwargs.get( 'detalle_unidades', 0 )
    detalle_costo_unitario = kwargs.get( 'detalle_costo_unitario', articulo.costo_ultima_compra )

    detalle_entradas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn = entrada ) )
    detalle_salidas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn = salida ) )
    articulo_clave = first_or_none( ClavesArticulos.objects.filter( articulo = articulo ) )

    detalle = DoctosInDet(
        articulo = articulo,
        claveArticulo = articulo_clave,
        almacen = almacen,
        unidades = detalle_unidades,
        costo_unitario = detalle_costo_unitario,
        )

    unidades_a_insertar = 0
    if detalle_entradas == None and detalle_salidas == None:
        entradas, salidas, existencias, inv_fin = get_existencias_articulo(
                articulo_id = articulo.id, 
                connection_name = connection_name, 
                fecha_inicio = datetime.now().strftime( "%m/01/%Y" ),
                almacen = detalle.almacen, )
        
        unidades_a_insertar = -inv_fin + detalle.unidades
        if inv_fin == 0:
            unidades_a_insertar = detalle.unidades

        detalle.id = next_id( 'ID_DOCTOS', connection_name )
        detalle.unidades_inv = detalle.unidades
        if detalle.unidades < 0:
            detalle.unidades_inv = - detalle.unidades

        detalle.unidades = unidades_a_insertar
    es_nuevo = False
    if detalle_unidades <= 0 or unidades_a_insertar < 0:
        # Si no existe un detalle de salida de ese articulo
        if detalle_salidas == None:
            es_nuevo = True
            detalle.id = next_id( 'ID_DOCTOS', connection_name )
            detalle.doctosIn = salida
            detalle.concepto = salida.concepto
            detalle.tipo_movto ='S'
            detalle_salidas = detalle
            detalle_salidas.unidades = -detalle_salidas.unidades
            detalle_salidas.unidades_inv = 0
        #si si existe
        elif detalle_salidas:
            detalle_salidas.unidades = (detalle_salidas.unidades + ( detalle.unidades * -1 ))

        detalle_salidas_unidades_inv =  detalle_salidas.unidades_inv

        if detalle_unidades < 0:
            detalle_salidas.unidades_inv = detalle_salidas.unidades_inv + detalle_unidades
        else:
            detalle_salidas.unidades_inv = detalle_salidas.unidades_inv + detalle_unidades
        

        detalle_salidas.costo_total = detalle_salidas.unidades * detalle_salidas.costo_unitario
        detalle_salidas.fechahora_ult_modif = datetime.now()
        if es_nuevo:
            detalle_salidas.save()
        else:    
            detalle_salidas.save( update_fields=[ 'unidades', 'unidades_inv', 'costo_total', 'fechahora_ult_modif',] );

    if detalle_unidades >= 0 and unidades_a_insertar >= 0:
        # Si no existe un detalle de salida de ese articulo
        if detalle_entradas == None:
            es_nuevo = True
            detalle.id = next_id( 'ID_DOCTOS', connection_name )
            detalle.doctosIn = entrada
            detalle.concepto = entrada.concepto
            detalle.tipo_movto ='E'
            if unidades_a_insertar > 0:
                detalle.unidades = unidades_a_insertar
            detalle_entradas = detalle
            detalle_entradas.unidades_inv = 0
        #si si existe
        elif detalle_entradas:
            detalle_entradas.unidades = detalle_entradas.unidades + detalle.unidades

        detalle_entradas.unidades_inv = detalle_entradas.unidades_inv + detalle_unidades
        detalle_entradas.costo_total = detalle_entradas.unidades * detalle_entradas.costo_unitario
        detalle_entradas.fechahora_ult_modif = datetime.now()

        # Para historial de modificaciones
        if detalle_entradas.detalle_modificaciones == None:
            detalle_entradas.detalle_modificaciones = ''
        if detalle_entradas.detalle_modificacionestime == None:
            detalle_entradas.detalle_modificacionestime = ''

        nuevo_texto = detalle_entradas.detalle_modificaciones + '[%s/%s=%s:%s],'%( request_user.username, ubicacion, detalle_unidades, detalle_costo_unitario )
        tamano_detalles = len( nuevo_texto )
        
        if tamano_detalles < 400:
            detalle_entradas.detalle_modificaciones = nuevo_texto
        else:
            message = "El numero de caracteres para detalles del articulo fue excedido"
        detalle_entradas.detalle_modificacionestime += '[%s/%s=%s:%s](%s),'%( request_user.username, ubicacion, detalle_unidades, detalle_costo_unitario, datetime.now().strftime("%d-%m-%Y %H:%M") )

        if es_nuevo:
            detalle_entradas.save()
        else:
            detalle_entradas.save( update_fields=[ 'unidades', 'unidades_inv', 'costo_total', 'fechahora_ult_modif', 'detalle_modificaciones', 'detalle_modificacionestime'] )

    c = connections[ connection_name ].cursor()
    c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo.id )
    c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo.id )
    transaction.commit_unless_managed()
    c.close()

    management.call_command( 'syncdb', database = connection_name )

    datos = {'error_message': '', 'alamcen_id': entrada.almacen.ALMACEN_ID, }
    
    return datos

@dajaxice_register( method = 'GET' )
def add_existenciasarticulo_byajustes_view( request, **kwargs ):
    """ Para agregar existencia a un articulo por ajuste"""
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    articulo_id = kwargs.get( 'articulo_id', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    salida_id = kwargs.get( 'salida_id', None )
    detalle_unidades = Decimal( kwargs.get( 'detalle_unidades', None ) )
    detalle_costo_unitario = Decimal( kwargs.get( 'detalle_costo_unitario', None ) )

    datos = add_existenciasarticulo_byajustes(
        articulo_id = articulo_id,
        entrada_id = entrada_id,
        salida_id = salida_id,
        detalle_unidades = detalle_unidades,
        detalle_costo_unitario = detalle_costo_unitario,
        request_session = request.session,
        request_user = request.user,
        ubicacion = ubicacion,
        )

    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia_bylinea( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    linea_id = kwargs.get( 'linea_id', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    salida_id = kwargs.get( 'salida_id', None )

    salida = DoctosIn.objects.get( pk = salida_id )
    entrada = DoctosIn.objects.get( pk = entrada_id )
    linea = LineaArticulos.objects.get( pk = linea_id )

    articulos_endocumentos = DoctosInDet.objects.filter( Q( doctosIn = entrada ) | Q( doctosIn = salida ) ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True )
    articulos_sinexistencia = Articulos.objects.filter( es_almacenable = 'S', linea = linea ).exclude( pk__in = articulos_endocumentos ).order_by( '-id' ).values_list( 'id', flat = True )
    
    total_articulos_sinexistencia = articulos_sinexistencia.count()
    articulos_sinexistencia = articulos_sinexistencia[0:9000]

    articulos_sinexistencia_list = split_seq( articulos_sinexistencia, 2000 )
    articulos_agregados = 0

    for articulos_sinexistencia_sublist in articulos_sinexistencia_list:
        detalles_en_ceros = 0
        for articulo_id in articulos_sinexistencia_sublist:
            
            add_existenciasarticulo_byajustes(
                    articulo_id = articulo_id ,
                    entrada_id = entrada_id,
                    salida_id = salida_id,
                    detalle_unidades = 0,
                    request_session = request.session,
                    request_user = request.user,
                    ubicacion = ubicacion,
                    )
            detalles_en_ceros = detalles_en_ceros + 1
            
        articulos_agregados = articulos_agregados + detalles_en_ceros

    articulos_pendientes = total_articulos_sinexistencia -  articulos_agregados
    return simplejson.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, } )

@dajaxice_register( method = 'GET' )
def get_existenciasarticulo_byclave( request, **kwargs ):
    """ Para obterner existencia de un articulo segun clave del articulo """
    #Paramentros
    almacen = kwargs.get( 'almacen', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    articulo_clave = kwargs.get( 'articulo_clave', None)
    connection_name = get_conecctionname( request.session )
    
    #variables de salida
    error = ""
    inv_fin = 0
    costo_ultima_compra = 0
    articulo_id = ''
    articulo_nombre = ''
    clave_articulo = first_or_none( ClavesArticulos.objects.filter( clave = articulo_clave ) )
    opciones_clave = {}
    
    detalle_modificaciones = ''
    detalle_modificacionestime = ''
    detalle_entradas_id = ''

    if clave_articulo:
        articulo = Articulos.objects.get( pk = clave_articulo.articulo.id )
        entradas, salidas, existencias, inv_fin = get_existencias_articulo(
            articulo_id = articulo.id,
            connection_name = connection_name, 
            fecha_inicio = datetime.now().strftime( "%m/01/%Y" ),
            almacen = almacen, )
        costo_ultima_compra = str(articulo.costo_ultima_compra)
        articulo_id = articulo.id
        articulo_nombre = articulo.nombre
        
        detalle_entradas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn__id = entrada_id ) )

        if detalle_entradas:
            detalle_modificaciones = detalle_entradas.detalle_modificaciones
            detalle_modificacionestime = detalle_entradas.detalle_modificacionestime
            detalle_entradas_id =  detalle_entradas.id

    else:
        error = "no_existe_clave"
        claves = ClavesArticulos.objects.filter( clave__contains = articulo_clave )
        for c in claves:
            opciones_clave[ str( c.clave ) ] = c.articulo.nombre
    
    datos = { 
        'error_msg' : error,
        'articulo_id' : articulo_id,
        'articulo_nombre' : articulo_nombre,
        'existencias' : str(inv_fin), 
        'costo_ultima_compra' : costo_ultima_compra,
        'opciones_clave': opciones_clave,
        'detalle_entradas_id' : detalle_entradas_id,
        'detalle_modificaciones' : detalle_modificaciones, 
        'detalle_modificacionestime': detalle_modificacionestime,
        }
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def get_existenciasarticulo_byid( request, **kwargs ):
    """ Para obterner existencia de un articulo segun id del articulo """
    #Paramentros
    almacen = kwargs.get( 'almacen', None)
    articulo_id = kwargs.get( 'articulo_id', None)
    entrada_id = kwargs.get( 'entrada_id', None )
    connection_name = get_conecctionname( request.session )
    
    articulo = Articulos.objects.get( pk = articulo_id )
    entradas, salidas, existencias, inv_fin = get_existencias_articulo(
        articulo_id = articulo_id , 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "%m/01/%Y" ),
        almacen = almacen, )
 
    detalle_entradas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn__id = entrada_id ) )
    
    detalle_modificaciones = ''
    detalle_modificacionestime = ''
    detalle_entradas_id = ''

    if detalle_entradas:
        detalle_modificaciones = detalle_entradas.detalle_modificaciones
        detalle_modificacionestime = detalle_entradas.detalle_modificacionestime
        detalle_entradas_id =  detalle_entradas.id

    return simplejson.dumps( { 
        'existencias' : int( inv_fin ), 
        'costo_ultima_compra' : str(articulo.costo_ultima_compra),
        'detalle_entradas_id' : detalle_entradas_id,
        'detalle_modificaciones' : detalle_modificaciones, 
        'detalle_modificacionestime': detalle_modificacionestime,
        })

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
