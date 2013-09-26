from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
import json
from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id
from microsip_web.libs.tools import split_seq

@dajaxice_register(method='GET')
def add_aticulosinventario(request, inventario_id, articulo_id, unidades, ubicacion):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
    else:
        conexion_activa_id = request.session['conexion_activa']

    conexion_name = "%02d-%s"%(conexion_activa_id, basedatos_activa)

    message = ''
    msg_series=''
    error = 0
    inicio_form = False
    movimiento = ''
    
    articulo_clave = ''
    articulos_claves =ClavesArticulos.objects.filter(articulo__id= articulo_id)
    if articulos_claves.count() > 0:
        articulo_clave = articulos_claves[0].clave

    try:
        doc = DoctosInvfisDet.objects.get(docto_invfis__id=inventario_id, articulo__id=articulo_id)
        str_unidades = unidades
        unidades = Decimal(unidades)
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
            id = next_id('ID_DOCTOS', conexion_name),
            docto_invfis = DoctosInvfis.objects.get(pk=inventario_id),
            clave = articulo_clave,
            unidades = unidades, 
            articulo = Articulos.objects.get(pk=articulo_id),
            usuario_ult_modif = request.user.username,
            detalle_modificaciones = '[%s/%s=%s], '%(request.user.username, ubicacion, unidades),
            )
    elif movimiento == 'actualizar':
        doc.fechahora_ult_modif = datetime.now()
        doc.unidades = unidades
        doc.clave = articulo_clave
        doc.usuario_ult_modif = request.user.username
        if doc.detalle_modificaciones == None:
            doc.detalle_modificaciones = ''
        tamano_detalles = len(doc.detalle_modificaciones + '[%s/%s=%s],'%(request.user.username, ubicacion, str_unidades))
    
        if  tamano_detalles  < 400:
            doc.detalle_modificaciones += '[%s/%s=%s],'%(request.user.username, ubicacion, str_unidades)
        else:
            message = "El numero de caracteres para detalles del articulo fue excedido"
        doc.save()

    return simplejson.dumps({'message':'exito'})

@dajaxice_register(method='GET')
def get_articulosen_inventario(request, inventario_id, articulo_id):
    detalle_modificaciones = ''
    try:
        doc = DoctosInvfisDet.objects.get(docto_invfis__id=inventario_id, articulo_id=articulo_id)
        unidades = doc.unidades
        detalle_modificaciones = doc.detalle_modificaciones
    except ObjectDoesNotExist:
        unidades = 0
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    return simplejson.dumps({'unidades':str(unidades), 'detalle_modificaciones':detalle_modificaciones, })

@dajaxice_register(method='GET')
def get_articulo_by_clave(request, clave):
    #se obtiene la provincia
    try:
        clave_articulo = ClavesArticulos.objects.get(clave=clave)
        articulo_id = clave_articulo.articulo.id
        articulo_nombre = clave_articulo.articulo.nombre
        articulo_seguimiento = clave_articulo.articulo.seguimiento
    except ObjectDoesNotExist:
        articulo_id = 0
        articulo_nombre = ''
        articulo_seguimiento = ''
    
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.

    return simplejson.dumps({'articulo_id':articulo_id, 'articulo_nombre':articulo_nombre, 'articulo_seguimiento':articulo_seguimiento, })


@dajaxice_register(method='GET')
def add_articulos_nocontabilizados_porlinea(request, inventario_id = None, linea_id= None):
    inventario_fisico = DoctosInvfis.objects.get(pk=inventario_id)
    linea = LineaArticulos.objects.get(pk=linea_id)
    articulos_enInventario = DoctosInvfisDet.objects.filter(docto_invfis=inventario_fisico).order_by('-articulo').values_list('articulo__id', flat=True)
    all_articulos_enceros = Articulos.objects.filter(es_almacenable='S',linea=linea).exclude(pk__in=articulos_enInventario).order_by('-id').values_list('id', flat=True)
    
    articulos_enceros = all_articulos_enceros[0:9000]

    articulos_enceros_list = split_seq(articulos_enceros, 2000)
    articulos_agregados = 0

    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter(articulo__id=articulo_id)
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario =DoctosInvfisDet(
                id=-1,
                docto_invfis= inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get(pk=articulo_id),
                unidades = 0)


            detalles_en_ceros.append(detalle_inventario)
        
        articulos_agregados = articulos_agregados + len(detalles_en_ceros)
        DoctosInvfisDet.objects.bulk_create(detalles_en_ceros)

    articulos_pendientes = all_articulos_enceros.count() -  articulos_agregados
    return simplejson.dumps({'articulos_agregados':articulos_agregados,'articulo_pendientes':articulos_pendientes,})

@dajaxice_register(method='GET')
def add_articulos_nocontabilizados(request, inventario_id = None):
    inventario_fisico = DoctosInvfis.objects.get(pk=inventario_id)
    articulos_enInventario = DoctosInvfisDet.objects.filter(docto_invfis=inventario_fisico).order_by('-articulo').values_list('articulo__id', flat=True)
    all_articulos_enceros = Articulos.objects.filter(es_almacenable='S').exclude(pk__in=articulos_enInventario).order_by('-id').values_list('id', flat=True)
    articulos_enceros = all_articulos_enceros[0:9000]
    articulos_enceros_list = split_seq(articulos_enceros, 2000)
    articulos_agregados = 0
    for articulos_enceros in articulos_enceros_list:
        detalles_en_ceros = []
        for articulo_id in articulos_enceros:
            clave_articulo = ClavesArticulos.objects.filter(articulo__id=articulo_id)
            if clave_articulo.count() <= 0:
                clave_articulo = ''
            else:
                clave_articulo = clave_articulo[0]

            detalle_inventario =DoctosInvfisDet(
                id=-1,
                docto_invfis= inventario_fisico,
                clave = clave_articulo,
                articulo = Articulos.objects.get(pk=articulo_id),
                unidades = 0)


            detalles_en_ceros.append(detalle_inventario)
    
        articulos_agregados = articulos_agregados + len(detalles_en_ceros)
        DoctosInvfisDet.objects.bulk_create(detalles_en_ceros)

    articulos_pendientes = all_articulos_enceros.count() -  articulos_agregados
    return simplejson.dumps({'articulos_agregados':articulos_agregados,'articulo_pendientes': articulos_pendientes,})