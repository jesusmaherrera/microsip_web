from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.main.comun.otros.paises.urls', namespace='paises')),
	url(r'', include('microsip_web.apps.main.comun.otros.estados.urls', namespace='estados')),
	url(r'', include('microsip_web.apps.main.comun.otros.ciudades.urls', namespace='ciudades')),
	url(r'', include('microsip_web.apps.main.comun.otros.tipos_cambio.urls', namespace='tipo_cambio')),
)