from django.conf.urls import patterns, url, include
from  microsip_web.settings.local_settings import MICROSIP_MODULES

urlpatterns = patterns('',
)
if 'microsip_web.apps.ventas.documentos' in MICROSIP_MODULES:
	urlpatterns +=	url(r'', include('microsip_web.apps.ventas.documentos.remisiones.urls', namespace='v_documentos_remisiones')),
	urlpatterns +=	url(r'', include('microsip_web.apps.ventas.documentos.facturas.urls', namespace='v_documentos_facturas')),
	urlpatterns += url(r'', include('microsip_web.apps.ventas.documentos.pedidos.urls', namespace='v_documentos_pedidos')),
else:
	if 'microsip_web.apps.ventas.documentos.remisiones' in MICROSIP_MODULES:
		urlpatterns +=	url(r'', include('microsip_web.apps.ventas.documentos.remisiones.urls', namespace='v_documentos_remisiones')),
	if 'microsip_web.apps.ventas.documentos.facturas' in MICROSIP_MODULES:
		urlpatterns +=	url(r'', include('microsip_web.apps.ventas.documentos.facturas.urls', namespace='v_documentos_facturas')),
	if 'microsip_web.apps.ventas.documentos.pedidos' in MICROSIP_MODULES:
		urlpatterns += url(r'', include('microsip_web.apps.ventas.documentos.pedidos.urls', namespace='v_documentos_pedidos')),