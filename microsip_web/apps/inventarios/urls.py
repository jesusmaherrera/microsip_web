from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.inventarios import views
from microsip_web.apps.punto_de_venta import views as pv_views

urlpatterns = patterns('',
    #INVENTARIOS FISICOS
    (r'^inventariosfisicos/$', views.invetariosfisicos_view),
    # (r'^InventarioFisico/$', views.invetarioFisico_manageView),
    # (r'^InventarioFisico/(?P<id>\d+)/', views.invetarioFisico_manageView),
    
    (r'^articulo/(?P<id>\d+)/', views.ArticuloManageView),
    (r'^inventariofisico/$', views.new_inventariofisico_ajustes),
    
    # (r'^inventariofisico/(?P<id>\d+)/', views.invetarioFisico_manageView),
    (r'^inventariofisico/(?P<id>\d+)/(?P<dua>\d+)/', views.invetarioFisico_manageView),
    (r'^inventarioFisico_mobile/(?P<id>\d+)/', views.invetarioFisico_mobile_pa_manageView),
    (r'^inventarioFisico_mobile/articulo_serie/(?P<id>\d+)/(?P<no_series>\d+)/', views.invetarioFisico_mobile_series_manageView),
    
    (r'^inventariofisico_ajustes/(?P<almacen_id>\d+)/$', views.invetariofisico_ajustes_manageview),
    (r'^inventariofisico_ajustesmobile/(?P<almacen_id>\d+)/$', views.invetariofisico_ajustesmobile_manageView),
    
    (r'^articulos/$', pv_views.articulos_view),
    (r'^almacenes/$', views.almacenes_view),

    (r'^articulo/(?P<id>\d+)/', pv_views.articulo_manageView),
    #(r'^InventarioFisico/Delete/(?P<id>\d+)/', views.invetarioFisico_delete),
    #ENTRADAS
    # (r'^Entradas/$', views.entradas_View),
    # (r'^Entrada/$', views.entrada_manageView),
    # (r'^Entrada/(?P<id>\d+)/', views.entrada_manageView),
    # (r'^Entrada/Delete/(?P<id>\d+)/', views.entrada_delete),
    #SALIDAS
    # (r'^Salidas/$', views.salidas_View),
    # (r'^Salida/$', views.salida_manageView),
    # (r'^Salida/(?P<id>\d+)/', views.salida_manageView),
    # (r'^Salida/Delete/(?P<id>\d+)/', views.salida_delete),
    
)