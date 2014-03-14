from django.conf.urls import patterns
from .views import facturas_view, factura_manageView

urlpatterns = patterns('',
	(r'^facturas/$', facturas_view),
	(r'^factura/$', factura_manageView),
	(r'^factura/(?P<id>\d+)/$', factura_manageView),
)