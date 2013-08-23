from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.shortcuts import get_object_or_404

from views import *
from models import *
from microsip_web.apps.main.models import *

@dajaxice_register(method='GET')
def crear_nodo(request, nombre, padre):
    conexion_activa =  request.user.userprofile.conexion_activa
    if conexion_activa == '':
        return HttpResponseRedirect('/select_db/')

    id = get_next_id_carpeta(conexion_activa)
    Carpeta.objects.using(conexion_activa).create(id=id, nombre=nombre, carpeta_padre=Carpeta.objects.using(conexion_activa).get(pk=padre))
    return simplejson.dumps({'id':id})

@dajaxice_register(method='GET')
def update_node(request, id, padre_id):
    conexion_activa =  request.user.userprofile.conexion_activa
    if conexion_activa == '':
        return HttpResponseRedirect('/select_db/')

    Carpeta.objects.using(conexion_activa).filter(id=id).update(carpeta_padre=Carpeta.objects.using(conexion_activa).get(pk=padre_id))
    return ''

@dajaxice_register(method='GET')
def rename_node(request, id, nombre):
    conexion_activa =  request.user.userprofile.conexion_activa
    if conexion_activa == '':
        return HttpResponseRedirect('/select_db/')

    Carpeta.objects.using(conexion_activa).filter(id=id).update(nombre=nombre)
    return ''

@dajaxice_register(method='GET')
def remove_node(request, id):
    conexion_activa =  request.user.userprofile.conexion_activa
    if conexion_activa == '':
        return HttpResponseRedirect('/select_db/')

    Carpeta.objects.using(conexion_activa).get(id = id).delete()
    return ''

@dajaxice_register(method='GET')
def create_articulocompatiblecarpeta(request, articulo_id, carpeta_id):
    conexion_activa =  request.user.userprofile.conexion_activa
    if conexion_activa == '':
        return HttpResponseRedirect('/select_db/')

    ArticuloCompatibleCarpeta.objects.using(conexion_activa).create(articulo=Articulos.objects.using(conexion_activa).get(pk=articulo_id), carpeta_compatible=Carpeta.objects.using(conexion_activa).get(pk=carpeta_id))
    return ''

