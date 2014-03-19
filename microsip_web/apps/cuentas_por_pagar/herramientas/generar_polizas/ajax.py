from dajaxice.decorators import dajaxice_register
from .models import PlantillaPolizas_CP
from django.core import serializers
from django.http import HttpResponse

@dajaxice_register(method='GET')
def obtener_plantillas_cp(request, tipo_plantilla):
    plantillas = PlantillaPolizas_CP.objects.filter(tipo=tipo_plantilla)
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    return HttpResponse(data, mimetype="application/javascript")

# @dajaxice_register(method='GET')
# def obtener_plantillas(request, tipo_plantilla):
#     #se obtiene la provincia
#     plantillas = []
#     if tipo_plantilla =='P' or tipo_plantilla == 'NC':
#     	plantillas = PlantillaPolizas_CP.objects.filter(tipo=tipo_plantilla)

#     #se devuelven las ciudades en formato json, solo nos interesa obtener como json
#     #el id y el nombre de las ciudades.
#     data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    

#     return HttpResponse(data, mimetype="application/javascript")


