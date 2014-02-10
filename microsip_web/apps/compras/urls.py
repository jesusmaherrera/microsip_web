from django.conf.urls import patterns, include, url

from documentos.compras import urls as compras_urls
from documentos.ordenes import urls as ordenes_urls

urlpatterns = patterns('',
	 url(r'', include(compras_urls)),
	 url(r'', include(ordenes_urls)),
)
