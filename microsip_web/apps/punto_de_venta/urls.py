from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.punto_de_venta import views

urlpatterns = patterns('',
	(r'^venta/$', views.venta_mostrador_manageView),
    (r'^venta/(?P<id>\d+)/', views.venta_mostrador_manageView),
	(r'^ventas/$', views.ventas_de_mostrador_view),
	(r'^devoluciones/$', views.devoluciones_de_ventas_view),

	(r'^GenerarPolizas/$', views.generar_polizas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    #(r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),

     #Puntos
    (r'^inicializar_puntos_clientes/$', views.inicializar_puntos_clientes),
    (r'^inicializar_puntos_articulos/$', views.inicializar_puntos_articulos),
    
    #Articulos
    (r'^articulos/$', views.articulos_view),
    (r'^articulo/(?P<id>\d+)/', views.articulo_manageView),
	#Clientes
	(r'^clientes/$', views.clientes_view),
	(r'^cliente/(?P<id>\d+)/', views.cliente_manageView),
    
    #Tipos Cliente
    (r'^tipos_cliente/$', views.tipos_cliente_view),
    (r'^tipo_cliente/(?P<id>\d+)/', views.tipo_cliente_manageView),

    (r'^cliente_search/', views.cliente_searchView),
    (r'^cliente_search/(?P<id>\d+)/', views.cliente_searchView),
    

    (r'^lineas_articulos/$', views.lineas_articulos_view),
	# (r'^linea_articulos/$', views.linea_articulos_manageView),
    (r'^linea_articulos/(?P<id>\d+)/', views.linea_articulos_manageView),
    
    (r'^grupos_lineas/$', views.grupos_lineas_view),
    # (r'^grupo_lineas/$', views.grupo_lineas_manageView),
    (r'^grupo_lineas/(?P<id>\d+)/', views.grupo_lineas_manageView),
)