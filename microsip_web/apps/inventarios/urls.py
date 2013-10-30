from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.inventarios import views
from microsip_web.apps.punto_de_venta import views as pv_views

urlpatterns = patterns('',
    #INVENTARIOS FISICOS
    # (r'^inventariosfisicos/$', views.invetariosfisicos_view),
    (r'^articulo/(?P<id>\d+)/', views.ArticuloManageView), 
    (r'^inventariofisico/(?P<almacen_id>\d+)/$', views.invetariofisico_manageview),
    (r'^inventariofisicomobile/(?P<almacen_id>\d+)/$', views.invetariofisicomobile_manageView),
    
    (r'^articulos/$', pv_views.articulos_view),
    (r'^almacenes/$', views.almacenes_view),

    (r'^articulo/(?P<id>\d+)/', pv_views.articulo_manageView),
    # (r'^preferencias/', views.preferencias_manageview),
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