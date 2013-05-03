from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from microsip_web.apps.inventarios.models import *
from django.core import serializers
from django.http import HttpResponse
from dajaxice.utils import deserialize_form

@dajaxice_register(method='GET')
def obtener_plantillas(request, tipo_plantilla):
    #se obtiene la provincia
    plantillas = []
    if tipo_plantilla =='P' or tipo_plantilla == 'NC':
    	plantillas = PlantillaPolizas_CP.objects.filter(tipo=tipo_plantilla)

    #se devuelven las ciudades en formato json, solo nos interesa obtener como json
    #el id y el nombre de las ciudades.
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    

    return HttpResponse(data, mimetype="application/javascript")


