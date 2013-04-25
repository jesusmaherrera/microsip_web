from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from inventarios.models import *
from django.core import serializers
from django.http import HttpResponse
from models import *
from cuentas_por_cobrar.models import PlantillaPolizas_CC

@dajaxice_register(method='GET')
def args_example(request, text):
    return simplejson.dumps({'message':'Your message is %s!' % text})

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

@dajaxice_register(method='GET')
def genera_polizas_cp(request, formulario):
    form = ExampleForm(deserialize_form(formulario))
    form = cuentas_por_pagar.generar_polizas_ajax(form)
    form = serializers.serialize("json", form)
    return HttpResponse(form, mimetype="application/javascript")
