from django.conf.urls import patterns
from .views import facturas_View

urlpatterns = patterns('',
	(r'^Facturas/$', facturas_View),
)