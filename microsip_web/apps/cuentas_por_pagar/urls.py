from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.cuentas_por_pagar.herramientas.urls', namespace='cp_herramientas')),
)