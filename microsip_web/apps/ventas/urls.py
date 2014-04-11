from django.conf.urls import patterns, url, include
INDEX_EXTEND = "ventas/base.html"
from microsip_web.settings.local_settings import MICROSIP_MODULES
from microsip_web.apps.main.comun.articulos.articulos.views import articulos_view

urlpatterns = patterns('',
	url(r'',articulos_view)
)

if 'microsip_web.apps.ventas.documentos' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.ventas.documentos.urls', namespace='v_documentos')),

if 'microsip_web.apps.ventas.herramientas' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.ventas.herramientas.urls', namespace='v_herramientas')),

if 'microsip_web.apps.main.comun.articulos' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.main.comun.articulos.urls', namespace='v_main_articulos')),

if 'microsip_web.apps.main.comun.clientes' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.main.comun.clientes.urls', namespace='v_main_clientes')),

if 'microsip_web.apps.main.comun.listas' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.main.comun.listas.urls', namespace='v_main_listas')),
	
if 'microsip_web.apps.main.comun.otros' in MICROSIP_MODULES:
	urlpatterns += url(r'', include('microsip_web.apps.main.comun.otros.urls', namespace='v_main_otros')),
