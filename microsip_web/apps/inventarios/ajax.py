from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
import json

from models import *

@dajaxice_register(method='GET')
def get_articulosen_inventario(request, inventario_id, articulo_id):
    try:
        doc = DoctosInvfisDet.objects.get(docto_invfis__id=inventario_id, articulo_id=articulo_id)
        unidades = doc.unidades
    except ObjectDoesNotExist:
        unidades = 0
    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.

    return simplejson.dumps({'unidades':unidades, })

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