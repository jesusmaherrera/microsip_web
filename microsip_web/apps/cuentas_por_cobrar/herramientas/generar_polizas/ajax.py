from dajaxice.decorators import dajaxice_register
from .models import PlantillaPolizas_CC
from django.core import serializers
from django.http import HttpResponse

@dajaxice_register(method='GET')
def obtener_plantillas_cc(request, tipo_plantilla):
    plantillas = PlantillaPolizas_CC.objects.filter(tipo=tipo_plantilla)
    data = serializers.serialize("json", plantillas, fields=('id','nombre'))
    return HttpResponse(data, mimetype="application/javascript")

