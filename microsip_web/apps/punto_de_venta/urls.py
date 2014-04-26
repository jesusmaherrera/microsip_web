from django.views import generic
from microsip_web.apps.punto_de_venta import views
from  microsip_web.settings.prod import MICROSIP_MODULES
from django.conf.urls import patterns, include, url
from microsip_web.apps.main.comun.articulos.articulos.views import articulos_view
urlpatterns = patterns('',    

	# (r'^venta/$', views.venta_mostrador_manageView),
 #    (r'^venta/(?P<id>\d+)/', views.venta_mostrador_manageView),
	# (r'^ventas/$', views.ventas_de_mostrador_view),
    #facturas
    (r'^main/$', articulos_view),
    (r'^facturas/$', views.facturas_view),
    (r'^factura/nueva/', views.factura_manageView),
    
    (r'^factura/(?P<id>\d+)/', views.factura_manageView),
    
	# (r'^devoluciones/$', views.devoluciones_de_ventas_view),

	(r'^GenerarPolizas/$', views.generar_polizas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
    
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    #(r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),

    #Articulos
    (r'^articulo/precio/', views.get_precio_articulo),
	
    #Categorias
    # (r'^categorias/$', views.categorias_view),
    # (r'^categorias/(?P<grupo_id>\d+)/$', views.categorias_view),
    # (r'^categoria/$', views.gruposgrupo_manageView),
    # (r'^categoria/(?P<categoria_id>\d+)/$', views.gruposgrupo_manageView),
    (r'^categoria/delete/None/(?P<categoria_id>\d+)/$', views.gruposgrupo_delete),
    (r'^categoria/delete/(?P<categoria_padre>\d+)/(?P<categoria_id>\d+)/$', views.gruposgrupo_delete),
    (r'^compatibilidadesArticulos/delete/(?P<articulo_id>\d+)/(?P<articuloCompatibleId>\d+)/$', views.ArticuloCompatibleArticulo_delete),
    (r'^compatibilidadesClasificaciones/delete/(?P<articulo_id>\d+)/(?P<articuloCompatibleId>\d+)/$', views.ArticuloCompatibleClasificacion_delete),
    
    #Tipos Cliente
    (r'^tipos_cliente/$', views.tipos_cliente_view),
    (r'^tipo_cliente/(?P<id>\d+)/', views.tipo_cliente_manageView),

    (r'^cliente_search/', views.cliente_searchView),
    (r'^cliente_search/(?P<id>\d+)/', views.cliente_searchView),
)

if 'microsip_web.apps.main.comun.articulos' in MICROSIP_MODULES:
    urlpatterns += url(r'', include('microsip_web.apps.main.comun.articulos.urls', namespace='v_main_articulos')),

if 'microsip_web.apps.main.comun.clientes' in MICROSIP_MODULES:
    urlpatterns += url(r'', include('microsip_web.apps.main.comun.clientes.urls', namespace='v_main_clientes')),

if 'microsip_web.apps.main.comun.listas' in MICROSIP_MODULES:
    urlpatterns += url(r'', include('microsip_web.apps.main.comun.listas.urls', namespace='v_main_listas')),
    
if 'microsip_web.apps.main.comun.otros' in MICROSIP_MODULES:
    urlpatterns += url(r'', include('microsip_web.apps.main.comun.otros.urls', namespace='v_main_otros')),