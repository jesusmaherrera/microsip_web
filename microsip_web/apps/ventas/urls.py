from django.conf.urls import patterns, url, include
from django.views import generic
from microsip_web.apps.ventas import views
from microsip_web.apps.punto_de_venta import views as pv_views

INDEX_EXTEND = "ventas/base.html"

urlpatterns = patterns('',
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	
	url(r'', include('microsip_web.apps.main.comun.otros.urls', namespace='v_main_otros')),
	url(r'', include('microsip_web.apps.main.comun.clientes.urls', namespace='v_main_clientes')),
    url(r'', include('microsip_web.apps.main.comun.listas.urls', namespace='v_main_listas')),
    url(r'', include('microsip_web.apps.main.comun.articulos.urls', namespace='v_main_articulos')),
	#Pedidos
	# (r'^pedidos/$', views.pedidos_view),
	# (r'^pedido/$', views.pedido_ManageView),
	# (r'^pedido/(?P<id>\d+)/$', views.pedido_ManageView),
	
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),

    #Articulos
    # (r'^articulo/(?P<id>\d+)/', pv_views.articulo_manageView),
)