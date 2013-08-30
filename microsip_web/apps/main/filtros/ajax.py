from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.shortcuts import get_object_or_404

from views import *
from models import *
from microsip_web.apps.main.models import *

@dajaxice_register(method='GET')
def crear_nodo(request, nombre, padre):
    basedatos_activa =  request.user.userprofile.basedatos_activa
    connecion_activa = ''
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')
    else:
        connecion_activa = request.user.userprofile.conexion_activa.id

    conexion_name = "%02d-%s"%(conexion_activa_id, basedatos_activa)

    id = get_next_id_carpeta(connection_name=conexion_name)
    Carpeta.objects.create(id=id, nombre=nombre, carpeta_padre=Carpeta.objects.get(pk=padre))
    return simplejson.dumps({'id':id})

@dajaxice_register(method='GET')
def update_node(request, id, padre_id):
    Carpeta.objects.filter(id=id).update(carpeta_padre=Carpeta.objects.get(pk=padre_id))
    return ''

@dajaxice_register(method='GET')
def rename_node(request, id, nombre):
    Carpeta.objects.filter(id=id).update(nombre=nombre)
    return ''

@dajaxice_register(method='GET')
def remove_node(request, id):
    Carpeta.objects.get(id = id).delete()
    return ''

@dajaxice_register(method='GET')
def create_articulocompatiblecarpeta(request, articulo_id, carpeta_id):
    ArticuloCompatibleCarpeta.objects.create(articulo=Articulos.objects.get(pk=articulo_id), carpeta_compatible=Carpeta.objects.get(pk=carpeta_id))
    return ''

