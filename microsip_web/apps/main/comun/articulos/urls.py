from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.main.comun.articulos.articulos.urls', namespace='articulos')),
	url(r'', include('microsip_web.apps.main.comun.articulos.lineas.urls', namespace='lineas')),
	url(r'', include('microsip_web.apps.main.comun.articulos.grupos.urls', namespace='grupos')),
)