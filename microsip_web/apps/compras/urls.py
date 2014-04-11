from django.conf.urls import patterns, include, url

from documentos.compras import urls as compras_urls
from documentos.ordenes import urls as ordenes_urls
from documentos.ordenes.views import ordenes_view
urlpatterns = patterns('',
	url(r'main/',ordenes_view),
	url(r'', include(compras_urls)),
	url(r'', include(ordenes_urls)),
)
