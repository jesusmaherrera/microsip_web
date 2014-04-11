from django.conf.urls import patterns, url, include
from herramientas.generar_polizas.views import generar_polizas_View
urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.cuentas_por_cobrar.herramientas.urls', namespace='cc_herramientas')),
	url(r'', generar_polizas_View),
)