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

    almacen = entrada.almacen
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
    if puede_modificar_costos and detalle.tipo_movto == 'E':
       detalle.costo_unitario = detalle_costo_unitario 
    else:
        detalle_costo_unitario = first_or_none( DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 27 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO'
            ).order_by('-fechahora_ult_modif').values_list( 'costo_unitario', flat = True ) )      
        
        if not detalle_costo_unitario:
            detalle_costo_unitario = articulo.costo_ultima_compra
    
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

    datos = {'error_message': '', 'alamcen_id': entrada.almacen.ALMACEN_ID, }
    
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


    if "Chrome" in request.META[ 'HTTP_USER_AGENT' ]:
       request.mobile = False

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

    #datos['is_mobile'] = request.mobile
    datos['is_mobile'] = True
    
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    salida_id = kwargs.get( 'salida_id', None )

    salida = DoctosIn.objects.get( pk = salida_id )
    entrada = DoctosIn.objects.get( pk = entrada_id )

    articulos_endocumentos = DoctosInDet.objects.filter( Q( doctosIn = entrada ) | Q( doctosIn = salida ) ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True )
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

    salida = DoctosIn.objects.get( pk = salida_id )
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
        entradas, salidas, existencias, inv_fin = get_existencias_articulo(
            articulo_id = articulo.id,
            connection_name = connection_name, 
            fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
            almacen = almacen_nombre, )
        
        articulo_id = articulo.id
        articulo_nombre = articulo.nombre
        articulo_seguimiento = articulo.seguimiento
        costo_ultima_compra = None

        detalles_all = DoctosInDet.objects.filter(
            Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
            articulo = articulo,
            almacen = almacen,
            doctosIn__descripcion = 'ES INVENTARIO').order_by('fechahora_ult_modif')

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
        
        if detalles_all:
            ya_ajustado = True

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

    detalles_all = DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
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
    if detalles_all:
        ya_ajustado = True

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
