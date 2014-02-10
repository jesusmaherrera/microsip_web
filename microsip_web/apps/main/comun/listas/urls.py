from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
	url(r'', include('microsip_web.apps.main.comun.listas.impuestos.urls', namespace='listas')),
)