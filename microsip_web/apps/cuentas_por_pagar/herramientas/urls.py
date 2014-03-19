from django.conf.urls import patterns, url, include
from  microsip_web.settings.local_settings import MICROSIP_MODULES


urlpatterns = patterns('',
)
if 'microsip_web.apps.cuentas_por_pagar.herramientas' in MICROSIP_MODULES:
	urlpatterns +=	url(r'', include('microsip_web.apps.cuentas_por_pagar.herramientas.generar_polizas.urls', namespace='cp_herramientas_generar_polizas')),
else:
	if 'microsip_web.apps.cuentas_por_pagar.herramientas.generar_polizas' in MICROSIP_MODULES:
		urlpatterns +=	url(r'', include('microsip_web.apps.cuentas_por_pagar.herramientas.generar_polizas.urls', namespace='cp_herramientas_generar_polizas')),