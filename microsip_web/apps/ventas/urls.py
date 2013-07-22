from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.ventas import views
from microsip_web.apps.punto_de_venta import views as pv_views

INDEX_EXTEND = "ventas/base.html"

urlpatterns = patterns('',
	(r'^Facturas/$', views.facturas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	
	#Pedidos
	(r'^pedidos/$', views.pedidos_view),
	(r'^pedido/$', views.pedido_ManageView),
	(r'^pedido/(?P<id>\d+)/$', views.pedido_ManageView),
	
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),

    #Articulos
    (r'^articulos/$', pv_views.articulos_view),
    (r'^articulo/(?P<id>\d+)/', pv_views.articulo_manageView),
)