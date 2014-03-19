from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.cuentas_por_cobrar.herramientas.urls', namespace='cc_herramientas')),
)