 #encoding:utf-8
import json
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core import management
import datetime, time
from django.db.models import Q
from mobi.decorators import detect_mobile
from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none
from microsip_web.libs.tools import split_seq
from django.db import connections, transaction
from microsip_web.libs.custom_db.main import get_conecctionname
from microsip_web.libs.inventarios import ajustar_existencias

from microsip_web.apps.config.models import DerechoUsuario
from microsip_web.settings.local_settings import MICROSIP_MODULES

@dajaxice_register( method = 'GET' )
def aplicar_doctoin( request, **kwargs ):
    doctoin_id = kwargs.get( 'doctoin_id', None )
    documento = DoctosIn.objects.get(pk=doctoin_id)
    documento.aplicado ='S'
    documento.save()
    return json.dumps( { 'msg' : 'ya'} )
    
def allow_microsipuser( username = None, clave_objeto=  None ):
    return DerechoUsuario.objects.filter(usuario__nombre = username, clave_objeto = clave_objeto).exists() or username == 'SYSDBA'

def ajustar_seriesinventario_byarticulo( **kwargs ):
    # Parametros
    msg = ''
    connection_name = kwargs.get('connection_name', None)
    unidades = kwargs.get('unidades', None)
    articulo = kwargs.get('articulo', None)
    articulo_clave = kwargs.get('articulo_clave', None)
    entrada = kwargs.get('entrada', None)
    almacen = kwargs.get('almacen', None)
    salida = kwargs.get('salida', None)
    request_username = kwargs.get('request_username', None)
    series = kwargs.get('series', None)
    ubicacion = kwargs.get('ubicacion', None)
    
    detalle = None
    #DETALLES ENTRADAS
    if unidades > 0:
        detalle = DoctosInDet.objects.get_or_create(articulo=articulo, doctosIn=entrada, defaults={
            'id': next_id('ID_DOCTOS', connection_name),
            'doctosIn': entrada,
            'almacen': entrada.almacen,
            'concepto': entrada.concepto,
            'tipo_movto': 'E',
            'claveArticulo': articulo_clave,
            'articulo': articulo,
            'unidades': 0,
            'usuario_ult_modif': request_username,
        })[0]

    #DETALLES SALIDAS
    if unidades < 0:    
        detalle = DoctosInDet.objects.get_or_create(
            articulo=articulo, doctosIn=salida,
            defaults={
                'id': next_id('ID_DOCTOS', connection_name),
                'doctosIn': salida,
                'almacen': salida.almacen,
                'concepto': salida.concepto,
                'tipo_movto': 'S',
                'claveArticulo': articulo_clave,
                'articulo': articulo,
                'unidades': 0,
                'usuario_ult_modif': request_username,
            })[0]

    for serie in series:
        articulo_discreto = ArticulosDiscretos.objects.get_or_create(
            clave=serie,
            articulo=articulo,
            tipo='S',
            defaults={'id': next_id('ID_CATALOGOS', connection_name), 
            })[0]

        if detalle.tipo_movto == 'E':
            
            if ExistDiscreto.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, almacen=almacen, articulo_discreto__clave=serie).exists():
                unidades =  unidades -1

            try:
                existencia_disc = ExistDiscreto.objects.get(articulo_discreto= articulo_discreto, almacen= almacen,)
            except ObjectDoesNotExist:
                ExistDiscreto.objects.create(id= next_id('ID_DOCTOS', connection_name), existencia= 1, articulo_discreto= articulo_discreto, almacen= almacen,)
            else:
                existencia_disc.existencia=1
                existencia_disc.save()

        elif detalle.tipo_movto == 'S':
            ExistDiscreto.objects.filter(articulo_discreto= articulo_discreto, almacen = almacen).update(existencia=0)
            
        DesgloseEnDiscretos.objects.get_or_create(
                    docto_in_det=detalle,
                    art_discreto=articulo_discreto,
                    defaults= {
                        'id': next_id('ID_DOCTOS', connection_name),
                        'unidades': 1,
                    },
                )

    if unidades < 0:
        unidades = - unidades    
    
    detalle.unidades = detalle.unidades + unidades
    detalle.costo_unitario = articulo.costo_ultima_compra
    detalle.costo_total = detalle.unidades * detalle.costo_unitario
    detalle.fechahora_ult_modif = datetime.now()

    if detalle.detalle_modificacionestime == None:
        detalle.detalle_modificacionestime = ''

    detalle.detalle_modificacionestime += '%s %s/%s=%s,'%( datetime.now().strftime("%d-%b-%Y %I:%M %p"), request_username, ubicacion, unidades)
    detalle.save( update_fields = [ 'unidades', 'fechahora_ult_modif','detalle_modificacionestime', ] )
    return msg

@dajaxice_register( method = 'GET' )
def add_seriesinventario_byarticulo( request, **kwargs ):
    # Parametros
    connection_name = get_conecctionname(request.session)
    error = False
    articulo_id = kwargs.get('articulo_id', None)
    articulo = Articulos.objects.get(pk=articulo_id)
    articulo_clave = first_or_none(
        ClavesArticulos.objects.filter(articulo=articulo))

    almacen_id = kwargs.get('almacen_id', None)
    almacen = Almacenes.objects.get(ALMACEN_ID=almacen_id)

    entrada_id = kwargs.get('entrada_id', None)
    entrada = DoctosIn.objects.get(pk=entrada_id)

    salida_id = kwargs.get('salida_id', None)
    salida = DoctosIn.objects.get(pk=salida_id)

    ubicacion = kwargs.get('ubicacion', None)
    unidades = kwargs.get('unidades', None)
    unidades = int(unidades)
    ajusteprimerconteo = almacen.inventario_conajustes

    series = kwargs.get('series', None)
    series = series.split(',')
    msg = ''

    existe_en_detalles = DoctosInDet.objects.filter(
        Q(doctosIn__concepto=27) | Q(doctosIn__concepto=38), articulo=articulo,
        almacen=almacen,
        doctosIn__descripcion='ES INVENTARIO',
        ).count() > 0

    #Checar numeros de serie
    for serie in series:
        if ExistDiscreto.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, almacen=almacen, articulo_discreto__clave=serie).exists() and serie != '' and unidades > 0 :
            #Si es la primera ves que se cuenta 
            if not ajusteprimerconteo or (ajusteprimerconteo and existe_en_detalles):
                msg = '%s El numero de serie %s ya esta registrado.' % (msg, serie)

        elif not ExistDiscreto.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, almacen=almacen, articulo_discreto__clave=serie).exists() and serie != '' and unidades < 0:
            msg = '%s El numero de serie %s no esta registrado.' % (msg, serie)
        if serie == '':
            series.remove(serie)
    
    if ajusteprimerconteo and not existe_en_detalles and unidades < 0:
        msg= 'No esta permitido ajustar en primer conteo a valores negativos'

    if msg == '':
        request_username = request.user.username
        #AJUSTAR SERIES
        if ajusteprimerconteo and not existe_en_detalles:
            existdiscretos_aeliminar = ExistDiscreto.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, almacen=almacen).exclude(articulo_discreto__clave__in=series)
            existdiscretos_aeliminar_count =existdiscretos_aeliminar.count()
            series_aeliminar = []
            for existdiscreto in existdiscretos_aeliminar:
                series_aeliminar.append(existdiscreto.articulo_discreto.clave)

            if existdiscretos_aeliminar_count > 0:
                msg = ajustar_seriesinventario_byarticulo(
                        connection_name = connection_name,
                        unidades = -existdiscretos_aeliminar_count,
                        articulo = articulo,
                        articulo_clave = articulo_clave,
                        entrada = entrada,
                        almacen = almacen,
                        salida = salida,
                        request_username = request_username,
                        series =  series_aeliminar,
                        ubicacion = ubicacion,
                    )
            
            msg = ajustar_seriesinventario_byarticulo(
                     connection_name = connection_name,
                     unidades = unidades,
                     articulo = articulo,
                     articulo_clave = articulo_clave,
                     entrada = entrada,
                     almacen = almacen,
                     salida = salida,
                     request_username = request_username,
                     series = series,
                     ubicacion = ubicacion,
                 )
        else:
           msg = ajustar_seriesinventario_byarticulo(
                    connection_name = connection_name,
                    unidades = unidades,
                    articulo = articulo,
                    articulo_clave = articulo_clave,
                    entrada = entrada,
                    almacen = almacen,
                    salida = salida,
                    request_username = request_username,
                    series = series,
                    ubicacion = ubicacion,
                )

        c = connections[ connection_name ].cursor()
        c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% articulo.id )
        c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% articulo.id )
        transaction.commit_unless_managed()
        c.close()
        management.call_command( 'syncdb', database = connection_name )

        if msg == '':
            msg = 'Movimiento registrado correctamente'
        
        exitencia = get_existencias_articulo(
            articulo_id = articulo.id, 
            connection_name = connection_name, 
            fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
            almacen = almacen, 
            )
    else:
        error = True
        exitencia =''
    return json.dumps( { 'msg' : msg, 'error': error,'articulo_nombre': articulo.nombre, 'existencia_actual':  str(exitencia),} ) 

@dajaxice_register( method = 'GET' )
def get_seriesinventario_byarticulo( request, **kwargs ):
    ''' Para ajustar un articulo a las unidades indicadas sin importar su existencia actual '''
    #Paramentros
    articulo_id = kwargs.get( 'articulo_id', None )
    almacen_id = kwargs.get( 'almacen_id', None )
    series = ''
    existenciadiscretos = ExistDiscreto.objects.filter(almacen__ALMACEN_ID = almacen_id, articulo_discreto__articulo__id = articulo_id, existencia__gt = 0)
        
    for existenciadiscreto in existenciadiscretos:
        series = "%s%s, "% (series, existenciadiscreto.articulo_discreto.clave)
    
    return json.dumps( { 'series' : series, } ) 



def add_existenciasarticulo_byajustes( **kwargs ):
    """ Para agregar existencia a un articulo por ajuste 
        En caso de que el articulo no tenga costo indicado [se le aplica el de la ultima compra]
    """

    #Paramentros
    ajustar_primerconteo = kwargs.get( 'ajustar_primerconteo', None )
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

    puede_modificar_costos = allow_microsipuser( username = request_user.username, clave_objeto = 469) and almacen.inventario_modifcostos

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
    existencia_inicial = ''
    #Si no se existe arituclo en documentos se ajustan unidades
    if not existe_en_detalles:
        existencia_inicial = get_existencias_articulo(
                articulo_id = articulo.id, 
                connection_name = connection_name, 
                fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
                almacen = almacen, 
            )  
        detalle.detalle_modificacionestime ='EXISTIN=%s / COSTOIN=%s,'%(existencia_inicial, articulo.costo_ultima_compra)
        
        if ajustar_primerconteo:
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
    
    costo_modificaciones = ''
    #MODIFICA COSTOS
    if puede_modificar_costos:
        if detalle.tipo_movto == 'E':
            detalle.costo_unitario = detalle_costo_unitario 
            #Afecta costo en articulo
            if articulo.costo_ultima_compra !=  detalle.costo_unitario:
                articulo.costo_ultima_compra = detalle.costo_unitario
                articulo.save(update_fields=['costo_ultima_compra',])
                costo_modificaciones = 'COSTO(%s)'%detalle.costo_unitario

        #si se ajusto el conteo pero en realidad se metieron unidades positivas cambia costo de compra
        if detalle.tipo_movto == 'S' and detalle_unidades >= 0:
            detalle.costo_unitario = detalle_costo_unitario 
            #Afecta costo en articulo
            if articulo.costo_ultima_compra !=  detalle.costo_unitario:
                articulo.costo_ultima_compra = detalle.costo_unitario
                articulo.save(update_fields=['costo_ultima_compra',])
                costo_modificaciones = 'COSTO(%s)'%detalle.costo_unitario
    else:
        #si el articulo no tiene costo de ultima compra se le manda en 0
        detalle.costo_unitario = articulo.costo_ultima_compra
        if not detalle.costo_unitario:
            detalle.costo_unitario = 0
    
    detalle.costo_total = detalle.unidades * detalle.costo_unitario
    detalle.fechahora_ult_modif = datetime.now()

    # HISTORIAL DE MODIFICACIONES
    if detalle.detalle_modificacionestime == None:
        detalle.detalle_modificacionestime = ''
    detalle_ajuste = '' 
    if not existe_en_detalles:   
        if ajustar_primerconteo:
            if detalle.tipo_movto == 'S':
                detalle_ajuste = '(AJ=-%s)'% detalle.unidades
            elif detalle.tipo_movto == 'E': 
                detalle_ajuste = '(AJ=%s)'% detalle.unidades

    detalle.detalle_modificacionestime += '%s %s/%s=%s%s%s,'%( datetime.now().strftime("%d-%b-%Y %I:%M %p"), request_user.username, ubicacion, detalle_unidades, detalle_ajuste, costo_modificaciones)

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

    exitencia = get_existencias_articulo(
        articulo_id = articulo.id, 
        connection_name = connection_name, 
        fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
        almacen = almacen, 
        )

    datos = {'error_message': '', 'alamcen_id': almacen.ALMACEN_ID, 'articulo_nombre': articulo.nombre, 'existencia_actual': str(exitencia) }
    
    return datos

@dajaxice_register( method = 'GET' )
def close_inventario_byalmacen_view( request, **kwargs ):
    """ Para agregar existencia a un articulo por ajuste"""
    #Paramentros
    almacen_id = kwargs.get( 'almacen_id', None )
    almacen = Almacenes.objects.get(pk= almacen_id)
    almacen.inventariando = False
    almacen.inventario_conajustes = False
    almacen.inventario_modifcostos = False
    almacen.save()

    DoctosIn.objects.filter(almacen__ALMACEN_ID = almacen_id, descripcion='ES INVENTARIO').update(descripcion= 'INVENTARIO CERRADO')

    return json.dumps( { 'mensaje' : 'Inventario cerrado', } ) 

@detect_mobile
@dajaxice_register( method = 'GET' )
def add_existenciasarticulo_byajustes_view( request, **kwargs ):
    """ Para agregar existencia a un articulo por ajuste"""
    #Paramentros
    ubicacion = kwargs.get( 'ubicacion', None )
    articulo_id = kwargs.get( 'articulo_id', None )
    entrada_id = kwargs.get( 'entrada_id', None )
    salida_id = kwargs.get( 'salida_id', None )
    is_mobile =  kwargs.get( 'is_mobile', False )
    detalle_unidades = Decimal( kwargs.get( 'detalle_unidades', None ) )
    detalle_costo_unitario = Decimal( kwargs.get( 'detalle_costo_unitario', None ) )
    entrada = DoctosIn.objects.get( pk = entrada_id )
    almacen_id = entrada.almacen.ALMACEN_ID

    ajustar_primerconteo = entrada.almacen.inventario_conajustes
    
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
            ajustar_primerconteo = ajustar_primerconteo,
        )


    datos['is_mobile'] = is_mobile
    
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

def inventario_getnew_folio():
    registro_folioinventario = Registry.objects.get( nombre = 'SIG_FOLIO_INVFIS' )
    folio = registro_folioinventario.valor 
    siguiente_folio = "%09d" % ( int( folio ) +1 )
    registro_folioinventario.valor = siguiente_folio
    registro_folioinventario.save()
    return folio

def add_articulos_sincontar( **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros 
    request_username = kwargs.get( 'request_username', None )
    connection_name = kwargs.get( 'connection_name', None )
    ubicacion = kwargs.get( 'ubicacion', None )
    linea = kwargs.get( 'linea', None )
    almacen = kwargs.get( 'almacen', None )
    
    message= ''
    
    articulos_endocumentos = list( set( DoctosInDet.objects.filter(
        Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
        almacen = almacen,
        doctosIn__descripcion = 'ES INVENTARIO'
        ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True ) ) )
    inventario_descripcion = ''
    #Para agregar los articulos de los documentos de inventarios como ya contados
    if linea:
        #VALIDACIONES
        if DoctosInvfis.objects.filter(descripcion= 'ARTICULOS SIN CONTAR', aplicado= 'N', almacen= almacen).exists():
            message = 'Ya se genero anteriormente un documento con articulos sin contar de todos los articulos, OPERACION RECHAZADA!!'
            return json.dumps( { 'articulos_agregados' : 0, 'articulo_pendientes' : 0, 'message': message, } )

        inventario_descripcion = 'ARTICULOS SIN CONTAR LINEA(%s)'% linea.nombre
        articulos_all = list( set( Articulos.objects.exclude(estatus = 'B').filter( es_almacenable = 'S', linea = linea ).order_by( '-id' ).values_list( 'id', flat = True ) ))
        
    else:
        inventario_descripcion = 'ARTICULOS SIN CONTAR'
        articulos_all = list( set( Articulos.objects.exclude( estatus = 'B').filter( es_almacenable = 'S').order_by( '-id' ).values_list( 'id', flat = True )))

    inventarios_fisicos =  DoctosInvfis.objects.filter(descripcion__contains= inventario_descripcion, aplicado= 'N', almacen= almacen)

    for inventario_fisico in inventarios_fisicos:
        articulos_endocumentosinv = (
                list( set( DoctosInvfisDet.objects.filter( docto_invfis = inventario_fisico, ).order_by( '-articulo' ).values_list( 'articulo__id', flat = True ) ) 
            )
        )

        articulos_endocumentos = articulos_endocumentos + articulos_endocumentosinv

    articulos_sincontar = [n for n in articulos_all if n not in articulos_endocumentos]
    total_articulos_sincontar = len(articulos_sincontar)
    articulos_sincontar = articulos_sincontar[0:9000]
    articulos_sincontar_list = split_seq( articulos_sincontar, 2000 )

    articulos_agregados = 0
    ultimofolio = Registry.objects.filter( nombre = 'SIG_FOLIO_INVFIS' )

    if total_articulos_sincontar <= 0:
        message = 'No hay articulos por agregar!!'
        return json.dumps( { 'articulos_agregados' : 0, 'articulo_pendientes' : 0, 'message': message, } )

    if not ultimofolio.exists():
        message = 'Para poder crear un inventario es nesesario Asignarles folios automaticos a los inventarios fisicos, OPERACION RECHAZADA!!'
        return json.dumps( { 'articulos_agregados' : 0, 'articulo_pendientes' : 0, 'message': message, } )

    inventario = DoctosInvfis.objects.create(
            id = next_id('ID_DOCTOS', connection_name),
            folio = inventario_getnew_folio(),
            fecha = datetime.now(),
            almacen = almacen,
            descripcion = inventario_descripcion,
            usuario_creador = request_username,
            usuario_aut_creacion = 'SYSDBA',
            usuario_ult_modif = request_username,
            usuario_aut_modif = 'SYSDBA',
        )

    for articulos_sincontar_sublist in articulos_sincontar_list:
        detalles_en_ceros = 0
        for articulo_id in articulos_sincontar_sublist:
            articulo = Articulos.objects.get(pk=articulo_id)
            DoctosInvfisDet.objects.create(
                    id = -1,
                    docto_invfis = inventario,
                    clave = first_or_none( ClavesArticulos.objects.filter( articulo = articulo ) ),
                    articulo = articulo,
                    unidades = 0,
                )
            detalles_en_ceros = detalles_en_ceros + 1

        articulos_agregados = articulos_agregados + detalles_en_ceros

    articulos_pendientes = total_articulos_sincontar -  articulos_agregados
    return json.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, 'message': message, } )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    connection_name = get_conecctionname(request.session)
    ubicacion = kwargs.get( 'ubicacion', None )
    almacen_id = kwargs.get( 'almacen_id', None )
    almacen = Almacenes.objects.get( pk= almacen_id )
    message= ''

    return add_articulos_sincontar(
            request_username = request.user.username,
            connection_name = connection_name,
            ubicacion = ubicacion,
            almacen = almacen,
        )

@dajaxice_register( method = 'GET' )
def add_articulossinexistencia_bylinea( request, **kwargs ):
    """ Agrega articulos almacenables de la linea indicada faltantes en los documentos de ajustes indicados.  """
    #Paramentros
    connection_name = get_conecctionname(request.session)
    ubicacion = kwargs.get( 'ubicacion', None )
    linea_id = kwargs.get( 'linea_id', None )
    almacen_id = kwargs.get( 'almacen_id', None )
    message= ''

    linea = LineaArticulos.objects.get( pk = linea_id )
    almacen = Almacenes.objects.get( pk= almacen_id )

    return add_articulos_sincontar( 
            request_username = request.user.username,
            connection_name= connection_name,
            ubicacion= ubicacion,
            linea = linea,
            almacen= almacen,
        )

    return json.dumps( { 'articulos_agregados' : articulos_agregados, 'articulo_pendientes' : articulos_pendientes, 'message': message, } )

@dajaxice_register( method = 'GET' )
def get_detallesarticulo_byid( request, **kwargs ):
    """ Selecionar un articulo por clave """
    #Paramentros
    articulo_id = kwargs.get( 'articulo_id', None)
    comun_name = kwargs.get( 'comun_name', None)
    articulo_clave = kwargs.get( 'articulo_clave', None)
    articulo = Articulos.objects.get( pk = articulo_id )

    if not articulo_clave:
        articulo_clave = first_or_none( ClavesArticulos.objects.filter( articulo_id = articulo_id, articulo__estatus = 'A'))
        if articulo_clave:
            articulo_clave = articulo_clave.clave

    datos = {
        'articulo_id': articulo.id,
        'articulo_nombre': articulo.nombre,
        'comun_name' : comun_name,
        'articulo_clave' : articulo_clave,
        'articulo_seguimiento': articulo.seguimiento,
        'articulo_costoultimacompra' : format(articulo.costo_ultima_compra, '.2f'),
    }

    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

@dajaxice_register( method = 'GET' )
def get_articulo_byclave( request, **kwargs ):
    """ Selecionar un articulo por clave """
    #Paramentros
    clave = kwargs.get( 'clave', None)
    comun_name = kwargs.get( 'comun_name', None)
    clave_articulo = first_or_none( ClavesArticulos.objects.filter( clave = clave, articulo__estatus = 'A'))

    articulo_id = ''
    articulo_nombre = ''
    
    #Para excluir claves de ariculos con lotes
    if clave_articulo:
        if clave_articulo.articulo.seguimiento == 'L':
            clave_articulo = None

    opciones_clave = {}
    
    if clave_articulo:
        articulo = Articulos.objects.get( pk = clave_articulo.articulo.id )
        articulo_id = articulo.id
        articulo_nombre = articulo.nombre
    else:
        claves = ClavesArticulos.objects.filter( clave__contains=clave, articulo__estatus='A',)
        for c in claves:
            if c.articulo.seguimiento == 'S' or c.articulo.seguimiento == 'N':
                opciones_clave[str(c.clave)] = c.articulo.nombre

    datos = {
        'articulo_id': articulo_id,
        'articulo_nombre': articulo_nombre,
        'comun_name' : comun_name,
        'opciones_clave': opciones_clave,
    }
    
    return HttpResponse( json.dumps( datos ), mimetype = "application/javascript" )

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
    articulo_linea = ''
    articulo_id = ''
    articulo_nombre = ''
    articulo_seguimiento = ''
    costo_ultima_compra= ''
    clave_articulo = first_or_none( ClavesArticulos.objects.filter( clave = articulo_clave, articulo__estatus = 'A'))
    
    if clave_articulo:
        if clave_articulo.articulo.seguimiento == 'L':
            clave_articulo = None
        
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

        inv_fin = get_existencias_articulo(
            articulo_id = articulo.id,
            connection_name = connection_name, 
            fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
            almacen = almacen_nombre, )
        
        articulo_id = articulo.id
        articulo_nombre = articulo.nombre
        try:
            articulo_linea = articulo.linea.nombre
        except ObjectDoesNotExist:
            articulo_linea = 'No indicada aun'

        articulo_seguimiento = articulo.seguimiento
        
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
            if not detalle_entradas.detalle_modificacionestime:
                detalle_entradas.detalle_modificacionestime =''
                
            detalle_modificacionestime = detalle_modificacionestime + detalle_entradas.detalle_modificacionestime
            
        for detalle_salidas in detalles_salidas:
            if not detalle_salidas.detalle_modificacionestime:
                detalle_salidas.detalle_modificacionestime = ''

            detalle_modificacionestime_salidas = detalle_modificacionestime_salidas + detalle_salidas.detalle_modificacionestime
            

        #si el articulo no tiene costo de ultima compra se le manda en 0
        costo_ultima_compra = articulo.costo_ultima_compra
        if not costo_ultima_compra:
            costo_ultima_compra = 0
    else:
        error = "no_existe_clave"
        claves = ClavesArticulos.objects.filter( clave__contains = articulo_clave, articulo__estatus='A',)
        for c in claves:
            if c.articulo.seguimiento == 'S' or c.articulo.seguimiento == 'N':
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
        'articulo_linea' : articulo_linea,
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

    inv_fin = get_existencias_articulo(
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

    for detalle_salidas in detalles_salidas:
        if not detalle_salidas.detalle_modificacionestime:
            detalle_salidas.detalle_modificacionestime = ''

        detalle_modificacionestime_salidas = detalle_modificacionestime_salidas + detalle_salidas.detalle_modificacionestime

    #si el articulo no tiene costo de ultima compra se le manda en 0
    costo_ultima_compra = articulo.costo_ultima_compra
    if not costo_ultima_compra:
        costo_ultima_compra = 0
    
    if not detalle_modificacionestime:
        detalle_modificacionestime = ''

    try:
        articulo_linea = articulo.linea.nombre
    except ObjectDoesNotExist:
        articulo_linea = 'No indicada aun'

    return json.dumps( { 
        'existencias' : int( inv_fin ), 
        'ya_ajustado': ya_ajustado,
        'articulo_seguimiento' : articulo.seguimiento,
        'costo_ultima_compra' : str(costo_ultima_compra),
        'detalle_modificacionestime': detalle_modificacionestime,
        'detalle_modificacionestime_salidas': detalle_modificacionestime_salidas,
        'articulo_linea' : articulo_linea
        })