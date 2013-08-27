from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.http import HttpResponse
import json

from models import *
from microsip_web.apps.cuentas_por_cobrar.models import PlantillaPolizas_CC
from microsip_web.apps.cuentas_por_pagar.models import PlantillaPolizas_CP
from microsip_web.apps.main.filtros.models import *
from microsip_web.apps.main.filtros.views import get_next_id_carpeta


@dajaxice_register(method='GET')
def args_example(request, text):
    return simplejson.dumps({'message':'Your message is %s!' % text})

@dajaxice_register(method='GET')
def get_infoarticulo(request, articulo_id):
    articulo = Articulos.objects.get(pk=articulo_id) 
    articulos_compatibles = ArticuloCompatibleArticulo.objects.filter(articulo=articulo)
    clasificaciones_compatibles = ArticuloCompatibleCarpeta.objects.filter(articulo=articulo)

    compatibles = ''
    for clas in clasificaciones_compatibles:
        compatibles = '%s [%s]'% (compatibles, clas.carpeta_compatible.nombre) 
    for art in articulos_compatibles:
        compatibles = '%s [%s]'% (compatibles, art.compatible_articulo.nombre) 

    return simplejson.dumps({'detalles':articulo.nota_ventas,'compatibilidades':compatibles,})

@dajaxice_register(method='GET')
def articulos_moveto(request, carpeta_id, articulos_seleccionados):
    for id in articulos_seleccionados:
        articulo = Articulos.objects.filter(pk=id).update(carpeta= Carpeta.objects.get(pk=carpeta_id))

    return simplejson.dumps({'message':'Your message is'})

@dajaxice_register(method='GET')
def get_articulosby_grupopadre(request, carpetapadre_id):
    articulos = Articulos.objects.filter(grupo_padre__id = carpetapadre_id)
    data = serializers.serialize("json", articulos,)
    return HttpResponse(data, mimetype="application/javascript")

@dajaxice_register(method='GET')
def get_gruposby_grupopadre(request, carpetapadre_id):
    grupos = Carpeta.objects.filter(carpeta_padre__id = Carpeta.objects.get(pk=carpetapadre_id).id)
    
    data = serializers.serialize("json", grupos, indent=4, relations=('grupo',))
    return HttpResponse(data, mimetype="application/javascript")

def buscar_hijos(data=[]):
    if data != None:
        hijos = Carpeta.objects.filter(carpeta_padre= Carpeta.objects.get(pk=data['attr']['id']))
    else:
        hijos = Carpeta.objects.filter(carpeta_padre= None)
    
    datoshijos = []
    for hijo in hijos:
        datahijo = {}
        datahijo['data'] = hijo.nombre
        datahijo['attr'] = {'id':hijo.id}
        datahijo = buscar_hijos(datahijo)
        datoshijos.append(datahijo)
    
    if data != None:
        data['children'] = datoshijos
    else:
        data = datoshijos
    return data

@dajaxice_register(method='GET')
def get_estructura_carpetas(request):
    datos = buscar_hijos(None)
    return HttpResponse(json.dumps(datos), mimetype="application/javascript")

@dajaxice_register(method='GET')
def get_articulosby_seccion(request, carpeta_id):
    articulos = Articulos.objects.filter(carpeta = Carpeta.objects.get(pk=carpeta_id) )
    
    data = serializers.serialize("json", articulos)
    return HttpResponse(data, mimetype="application/javascript")

@dajaxice_register(method='GET')
def obtener_plantillas(request, tipo_plantilla):
    #se obtiene la provincia
    plantillas = []
    if tipo_plantilla =='F' or tipo_plantilla == 'D':
    	plantillas = PlantillaPolizas_V.objects.filter(tipo=tipo_plantilla)

    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    

    return HttpResponse(data, mimetype="application/javascript")

@dajaxice_register(method='GET')
def obtener_plantillas_cp(request, tipo_plantilla):
    #se obtiene la provincia
    
    plantillas = PlantillaPolizas_CP.objects.filter(tipo=tipo_plantilla)

    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    

    return HttpResponse(data, mimetype="application/javascript")

@dajaxice_register(method='GET')
def obtener_plantillas_cc(request, tipo_plantilla):
    #se obtiene la provincia
    
    plantillas = PlantillaPolizas_CC.objects.filter(tipo=tipo_plantilla)

    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    

    return HttpResponse(data, mimetype="application/javascript")

