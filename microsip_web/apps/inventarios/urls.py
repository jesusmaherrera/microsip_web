from django.conf.urls import patterns, url, include
from django.views import generic
from microsip_web.apps.inventarios import views
from microsip_web.apps.punto_de_venta import views as pv_views

urlpatterns = patterns('',
    #INVENTARIOS FISICOS
    # (r'^inventariosfisicos/$', views.invetariosfisicos_view),
    (r'^articulo/(?P<id>\d+)/', views.ArticuloManageView), 
    (r'^inventariofisico/(?P<almacen_id>\d+)/$', views.invetariofisico_manageview),
    (r'^inventariofisicomobile/(?P<almacen_id>\d+)/$', views.invetariofisicomobile_manageView),
    
    
    (r'^almacenes/$', views.almacenes_view),
    (r'main/', views.almacenes_view),
    (r'^almacenes/abririnventario/(?P<almacen_id>\d+)/$', views.abrir_inventario_byalmacen),
    
    url(r'', include('microsip_web.apps.main.comun.articulos.urls', namespace='in_main_articulos')),
    (r'^articulo/(?P<id>\d+)/', pv_views.articulo_manageView),
    #(r'^InventarioFisico/Delete/(?P<id>\d+)/', views.invetarioFisico_delete),
    #ENTRADAS
    (r'^entradas/$', views.entradas_View),
    (r'^entrada/$', views.entrada_manageView),
    (r'^entrada/(?P<id>\d+)/', views.entrada_manageView),
    # (r'^Entrada/Delete/(?P<id>\d+)/', views.entrada_delete),
    #SALIDAS
    # (r'^Salidas/$', views.salidas_View),
    # (r'^Salida/$', views.salida_manageView),
    # (r'^Salida/(?P<id>\d+)/', views.salida_manageView),
    # (r'^Salida/Delete/(?P<id>\d+)/', views.salida_delete),
    
)