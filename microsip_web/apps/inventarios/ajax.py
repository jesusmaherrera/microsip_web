from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
import json

from models import *
from microsip_web.libs.tools import split_seq

@dajaxice_register(method='GET')
def get_articulosen_inventario(request, inventario_id, articulo_id):
    try:
        doc = DoctosInvfisDet.objects.get(docto_invfis__id=inventario_id, articulo_id=articulo_id)
        unidades = doc.unidades
    except ObjectDoesNotExist:
        unidades = 0
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.

    return simplejson.dumps({'unidades':str(unidades), })

@dajaxice_register(method='GET')
def get_articulo_by_clave(request, clave):
    #se obtiene la provincia
    try:
        clave_articulo = ClavesArticulos.objects.get(clave=clave)
        articulo_id = clave_articulo.articulo.id
        articulo_nombre = clave_articulo.articulo.nombre
        
    except ObjectDoesNotExist:
        articulo_id = 0
        articulo_nombre =''
    
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.

    return simplejson.dumps({'articulo_id':articulo_id,'articulo_nombre':articulo_nombre,})


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