from django.conf.urls import patterns
from .views import pedidos_view, pedido_manageview

urlpatterns = patterns('',
	(r'^pedidos/$', pedidos_view),
	(r'^pedido/$', pedido_manageview),
	(r'^pedido/(?P<id>\d+)/$', pedido_manageview),
)