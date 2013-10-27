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
from mobi.decorators import detect_mobile
from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none
from microsip_web.libs.tools import split_seq
from django.db import connections, transaction
from microsip_web.libs.custom_db.main import get_conecctionname
from microsip_web.apps.config.models import DerechoUsuario

def allow_microsipuser( username = None, clave_objeto=  None ):
    return DerechoUsuario.objects.filter(usuario__nombre = username, clave_objeto = clave_objeto).exists() or username == 'SYSDBA'

def ajustar_existencias( **kwargs ):
    ''' Para ajustar un articulo a las unidades indicadas sin importar su existencia actual '''
    #Paramentros
    articulo_id = kwargs.get( 'articulo_id', None )
    ajustar_a = kwargs.get( 'ajustar_a', None )
    almacen = kwargs.get( 'almacen', None )
    connection_name = kwargs.get( 'connection_name', None )

    entradas, salidas, existencias, inv_fin = get_existencias_articulo(
        articulo_id = articulo_id, 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
        almacen = almacen, 
        )

    unidades_a_insertar = -inv_fin + ajustar_a

    return unidades_a_insertar

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
    salida_id = kwargs.get( 'salida_id', None )
    salida = DoctosIn.objects.get( pk = salida_id )
    
    almacen_id = kwargs.get( 'almacen_id', None )
    almacen = Almacenes.objects.get( pk = almacen_id)

    request_session = kwargs.get( 'request_session', 0 )
    request_user = kwargs.get( 'request_user', 0 )
    connection_name = get_conecctionname( request_session )
    
    detalle_unidades = kwargs.get( 'detalle_unidades', 0 )
    detalle_costo_unitario = kwargs.get( 'detalle_costo_unitario', articulo.costo_ultima_compra )
    
    puede_modificar_costos = allow_microsipuser( username = request_user.username, clave_objeto = 469)

    detalles_entradas_ultimocosto = first_or_none( DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 27 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO'
            ).order_by('-fechahora_ult_modif').values_list( 'costo_unitario', flat = True ) )

    if not detalles_entradas_ultimocosto:
         detalles_entradas_ultimocosto = articulo.costo_ultima_compra

    existe_en_detalles = DoctosInDet.objects.filter( 
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
        articulo = articulo,
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO',
        ).count() > 0

    detalle_entradas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn = entrada ) )
    detalle_salidas = first_or_none( DoctosInDet.objects.filter( articulo = articulo, doctosIn = salida ) )
    articulo_clave = first_or_none( ClavesArticulos.objects.filter( articulo = articulo ) )

    detalle = DoctosInDet(
        articulo = articulo,
        claveArticulo = articulo_clave,
        almacen = almacen,
        unidades = detalle_unidades,
        )
    
    #Logica

    #Si no se existe arituclo en documentos se ajustan unidades
    if not existe_en_detalles:
        detalle.unidades = ajustar_existencias( articulo_id = articulo.id, ajustar_a = detalle.unidades ,almacen = almacen , connection_name = connection_name )

    es_nuevo = False

    #SALIDA
    if detalle.unidades <= 0:
        #si no existe detalle salidas
        if not detalle_salidas:
            es_nuevo = True
            detalle_salidas = detalle
            detalle_salidas.id = next_id( 'ID_DOCTOS', connection_name )
            detalle_salidas.doctosIn = salida
            detalle_salidas.concepto = salida.concepto
            detalle_salidas.tipo_movto ='S'
            detalle_salidas.unidades = -detalle_salidas.unidades
        #Si exitse detalle salidas
        elif detalle_salidas:
            detalle_salidas.unidades = detalle_salidas.unidades + ( -detalle.unidades ) 

        #Desde salida no se permite cambiar costo unitario
        detalle_salidas.costo_unitario = detalles_entradas_ultimocosto
        detalle = detalle_salidas
    
    #ENTRADA
    elif detalle.unidades > 0:
        if not detalle_entradas:
            es_nuevo = True
            detalle_entradas = detalle
            detalle_entradas.id = next_id( 'ID_DOCTOS', connection_name )
            detalle_entradas.doctosIn = entrada
            detalle_entradas.concepto = entrada.concepto
            detalle_entradas.tipo_movto ='E'

        elif detalle_entradas:
            detalle_entradas.unidades = detalle_entradas.unidades + detalle.unidades
            
        detalle = detalle_entradas
    
    #MODIFICA COSTOS
    #Si es entrada y tiene pribilegios modifica el costo unitario
    # if puede_modificar_costos and detalle.tipo_movto == 'E':
    #    detalle.costo_unitario = detalle_costo_unitario 
    # else:
    # detalle_costo_unitario = first_or_none( DoctosInDet.objects.filter(
    #     Q( doctosIn__concepto = 27 ),
    #     articulo = articulo,
    #     almacen = almacen,
    #     doctosIn__descripcion = 'ES INVENTARIO'
    #     ).order_by('-fechahora_ult_modif').values_list( 'costo_unitario', flat = True ) )      
    
    # if not detalle_costo_unitario:
    detalle_costo_unitario = articulo.costo_ultima_compra
    detalle.costo_unitario = detalle_costo_unitario
    detalle.costo_total = detalle.unidades * detalle.costo_unitario
    detalle.fechahora_ult_modif = datetime.now()

    # HISTORIAL DE MODIFICACIONES
    if detalle.detalle_modificacionestime == None:
        detalle.detalle_modificacionestime = ''
    detalle_ajuste = '' 
    if not existe_en_detalles:   
        detalle_ajuste = '(AJ.=%s)'%detalle.unidades
    detalle.detalle_modificacionestime += '%s %s/%s=%s%s $%s,'%( datetime.now().strftime("%d-%b-%Y %I:%M %p"), request_user.username, ubicacion, detalle_unidades, detalle_ajuste, detalle.costo_unitario )

    if es_nuevo:
        detalle.save()
    else:    
        detalle.save( update_fields = [ 'unidades', 'costo_unitario', 'costo_total', 'fechahora_ult_modif','detalle_modificacionestime', ] );

    c = connections[ connection_name ].cursor()
    c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo.id )
    c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo.id )
    transaction.commit_unless_managed()
    c.close()

    management.call_command( 'syncdb', database = connection_name )

    datos = {'error_message': '', 'alamcen_id': almacen.ALMACEN_ID, }
    
    return datos

@dajaxice_register( method = 'GET' )
def close_inventario_byalmacen_view( request, **kwargs ):
    """ Para agregar existencia a un articulo por ajuste"""
    #Paramentros
    almacen_id = kwargs.get( 'almacen_id', None )
    DoctosIn.objects.filter(almacen__ALMACEN_ID = almacen_id, descripcion='ES INVENTARIO').update(descripcion= 'INVENTARIO CERRADO')
    return simplejson.dumps( { 'mensaje' : 'Inventario cerrado', } ) 

@detect_mobile
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
    entrada = DoctosIn.objects.get( pk = entrada_id )
    almacen_id = entrada.almacen.ALMACEN_ID

    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False

    #Para dos almacenes
    entrada2_id = kwargs.get( 'entrada2_id', None )
    salida2_id = kwargs.get( 'salida2_id', None )
    almacen_sinventas = first_or_none( Almacenes.objects.filter( nombre = 'Almacen sin ventas' ))
    if almacen_sinventas and entrada2_id and salida2_id:

        add_existenciasarticulo_byajustes(
        articulo_id = articulo_id,
        entrada_id = entrada2_id,
        salida_id = salida2_id,
        detalle_unidades = detalle_unidades,
        request_session = request.session,
        request_user = request.user,
        ubicacion = ubicacion,
        almacen_id = almacen_sinventas.ALMACEN_ID,
        )

    datos = add_existenciasarticulo_byajustes(
        articulo_id = articulo_id,
        entrada_id = entrada_id,
        salida_id = salida_id,
        detalle_unidades = detalle_unidades,
        detalle_costo_unitario = detalle_costo_unitario,
        request_session = request.session,
        request_user = request.user,
        ubicacion = ubicacion,
        almacen_id = almacen_id,
        )


    datos['is_mobile'] = request.mobile
    
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    entrada = DoctosIn.objects.get( pk = entrada_id )
    almacen = entrada.almacen

    salida_id = kwargs.get( 'salida_id', None )

    salida = DoctosIn.objects.get( pk = salida_id )
    entrada = DoctosIn.objects.get( pk = entrada_id )

    articulos_endocumentos = list( set( DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO'
        ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True ) ) )
    articulos_sinexistencia = Articulos.objects.exclude( estatus = 'B').filter( es_almacenable = 'S', seguimiento='N').exclude(pk__in = articulos_endocumentos ).order_by( '-id' ).values_list( 'id', flat = True )
    
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
                    almacen_id = almacen.ALMACEN_ID,
                    )
            detalles_en_ceros = detalles_en_ceros + 1
            
        articulos_agregados = articulos_agregados + detalles_en_ceros

    articulos_pendientes = total_articulos_sinexistencia -  articulos_agregados
    return simplejson.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, } )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia_bylinea( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    linea_id = kwargs.get( 'linea_id', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    salida_id = kwargs.get( 'salida_id', None )

    entrada = DoctosIn.objects.get( pk = entrada_id )
    linea = LineaArticulos.objects.get( pk = linea_id )
    almacen = entrada.almacen

    articulos_endocumentos = list( set( DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO'
        ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True ) ) )

    articulos_sinexistencia = Articulos.objects.exclude(estatus = 'B').filter( es_almacenable = 'S', seguimiento='N', linea = linea ).exclude(pk__in = articulos_endocumentos ).order_by( '-id' ).values_list( 'id', flat = True )
    
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
                    almacen_id = almacen.ALMACEN_ID
                    )
            detalles_en_ceros = detalles_en_ceros + 1
            
        articulos_agregados = articulos_agregados + detalles_en_ceros

    articulos_pendientes = total_articulos_sinexistencia -  articulos_agregados
    return simplejson.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, } )

@dajaxice_register( method = 'GET' )
def get_existenciasarticulo_byclave( request, **kwargs ):
    """ Para obterner existencia de un articulo segun clave del articulo """
    #Paramentros
    almacen_nombre = kwargs.get( 'almacen', None)
    almacen = Almacenes.objects.get(nombre = almacen_nombre)
    entrada_id = kwargs.get( 'entrada_id', None )
    articulo_clave = kwargs.get( 'articulo_clave', None)
    connection_name = get_conecctionname( request.session )
    
    #variables de salida
    error = ""
    inv_fin = 0
    costo_ultima_compra = 0
    articulo_id = ''
    articulo_nombre = ''
    articulo_seguimiento = ''
    clave_articulo = first_or_none( ClavesArticulos.objects.exclude( articulo__estatus = 'B').filter( clave = articulo_clave, articulo__seguimiento = 'N' ) )
    opciones_clave = {}
    
    detalle_modificacionestime = ''
    detalle_modificacionestime_salidas = ''
    ya_ajustado = False
    if clave_articulo:
        articulo = Articulos.objects.get( pk = clave_articulo.articulo.id )

        detalles_all = DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')
        
        if detalles_all:
            ya_ajustado = True
        else:
            c = connections[ connection_name ].cursor()
            c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo.id )
            c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo.id )
            transaction.commit_unless_managed()
            c.close()

            management.call_command( 'syncdb', database = connection_name )

        entradas, salidas, existencias, inv_fin = get_existencias_articulo(
            articulo_id = articulo.id,
            connection_name = connection_name, 
            fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
            almacen = almacen_nombre, )
        
        articulo_id = articulo.id
        articulo_nombre = articulo.nombre
        articulo_seguimiento = articulo.seguimiento
        costo_ultima_compra = None

        detalles_entradas = DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 27 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO'
            ).order_by('fechahora_ult_modif')

        detalles_salidas = DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 38 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')

        for detalle_entradas in detalles_entradas:
            detalle_modificacionestime = detalle_modificacionestime + detalle_entradas.detalle_modificacionestime
            costo_ultima_compra = detalle_entradas.costo_unitario
        
        for detalle_salidas in detalles_salidas:
            if not detalle_salidas.detalle_modificacionestime:
                detalle_salidas.detalle_modificacionestime = ''

            detalle_modificacionestime_salidas = detalle_modificacionestime_salidas + detalle_salidas.detalle_modificacionestime
            #costo_ultima_compra = detalle_salidas.costo_unitario
        


        #Si no existe un costo ya asignado se asigna el del articulo    
        if not costo_ultima_compra:
            costo_ultima_compra = str(articulo.costo_ultima_compra)
    else:
        error = "no_existe_clave"
        claves = ClavesArticulos.objects.exclude(articulo__estatus='B').filter( clave__contains = articulo_clave, articulo__seguimiento = 'N' )
        for c in claves:
            opciones_clave[ str( c.clave ) ] = c.articulo.nombre
    
    if not detalle_modificacionestime:
        detalle_modificacionestime = ''

    datos = { 
        'error_msg' : error,
        'ya_ajustado': ya_ajustado,
        'articulo_id' : articulo_id,
        'articulo_seguimiento': articulo_seguimiento,
        'articulo_nombre' : articulo_nombre,
        'existencias' : str(inv_fin), 
        'costo_ultima_compra' : str(costo_ultima_compra),
        'opciones_clave': opciones_clave,
        'detalle_modificacionestime': detalle_modificacionestime,
        'detalle_modificacionestime_salidas': detalle_modificacionestime_salidas,
        }
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def get_existenciasarticulo_byid( request, **kwargs ):
    """ Para obterner existencia de un articulo segun id del articulo """
    #Paramentros
    almacen_nombre = kwargs.get( 'almacen', None)
    almacen = Almacenes.objects.get(nombre = almacen_nombre)
    articulo_id = kwargs.get( 'articulo_id', None)
    entrada_id = kwargs.get( 'entrada_id', None )
    connection_name = get_conecctionname( request.session )
    detalle_modificacionestime = ''
    detalle_modificacionestime_salidas = ''
    ya_ajustado = False
    costo_ultima_compra = None
    
    articulo = Articulos.objects.get( pk = articulo_id )

    detalles_all = DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
        articulo = articulo,
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')

    if detalles_all:
        ya_ajustado = True
    else:
        c = connections[ connection_name ].cursor()
        c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo.id )
        c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo.id )
        transaction.commit_unless_managed()
        c.close()

        management.call_command( 'syncdb', database = connection_name )

    entradas, salidas, existencias, inv_fin = get_existencias_articulo(
        articulo_id = articulo_id , 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
        almacen = almacen_nombre, )
 
    detalles_entradas = DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ),
        articulo = articulo,
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')

    detalles_salidas = DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 38 ),
        articulo = articulo,
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')

    for detalle_entradas in detalles_entradas:
        if not detalle_entradas.detalle_modificacionestime:
            detalle_entradas.detalle_modificacionestime = ''

        detalle_modificacionestime = detalle_modificacionestime + detalle_entradas.detalle_modificacionestime
        costo_ultima_compra = detalle_entradas.costo_unitario

    for detalle_salidas in detalles_salidas:
        if not detalle_salidas.detalle_modificacionestime:
            detalle_salidas.detalle_modificacionestime = ''

        detalle_modificacionestime_salidas = detalle_modificacionestime_salidas + detalle_salidas.detalle_modificacionestime
        #costo_ultima_compra = detalle_salidas.costo_unitario

    #Si no existe un costo ya asignado se asigna el del articulo    
    if not costo_ultima_compra:
        costo_ultima_compra = str(articulo.costo_ultima_compra)
    
    if not detalle_modificacionestime:
        detalle_modificacionestime = ''

    return simplejson.dumps( { 
        'existencias' : int( inv_fin ), 
        'ya_ajustado': ya_ajustado,
        'articulo_seguimiento' : articulo.seguimiento,
        'costo_ultima_compra' : str(costo_ultima_compra),
        'detalle_modificacionestime': detalle_modificacionestime,
        'detalle_modificacionestime_salidas': detalle_modificacionestime_salidas,
        })