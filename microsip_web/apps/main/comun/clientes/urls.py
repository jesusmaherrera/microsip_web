from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.main.comun.clientes.clientes.urls', namespace='Clientes')),
	url(r'', include('microsip_web.apps.main.comun.clientes.condiciones_de_pago.urls', namespace='condiciones_de_pago')),
)