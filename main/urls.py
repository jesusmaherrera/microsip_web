from django.conf.urls import patterns, url
from django.views import generic
from main import views

urlpatterns = patterns('',
    (r'^lineas_articulos/$', views.lineas_articulos_view),
	# (r'^linea_articulos/$', views.linea_articulos_manageView),
    (r'^linea_articulos/(?P<id>\d+)/', views.linea_articulos_manageView),
    
    (r'^grupos_lineas/$', views.grupos_lineas_view),
    # (r'^grupo_lineas/$', views.grupo_lineas_manageView),
    (r'^grupo_lineas/(?P<id>\d+)/', views.grupo_lineas_manageView),
    # (r'^InventarioFisico/$', views.invetarioFisico_manageView),
    # (r'^InventarioFisico/(?P<id>\d+)/', views.invetarioFisico_manageView),
    # (r'^InventarioFisico/Delete/(?P<id>\d+)/', views.invetarioFisico_delete),
)