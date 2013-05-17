from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.inventarios import views

urlpatterns = patterns('',
    #INVENTARIOS FISICOS
    (r'^InventariosFisicos/$', views.invetariosFisicos_View),
    (r'^InventarioFisico/$', views.invetarioFisico_manageView),
    (r'^InventarioFisico/(?P<id>\d+)/', views.invetarioFisico_manageView),
    (r'^InventarioFisico/Delete/(?P<id>\d+)/', views.invetarioFisico_delete),
    #ENTRADAS
    (r'^Entradas/$', views.entradas_View),
    (r'^Entrada/$', views.entrada_manageView),
    (r'^Entrada/(?P<id>\d+)/', views.entrada_manageView),
    (r'^Entrada/Delete/(?P<id>\d+)/', views.entrada_delete),
    #SALIDAS
    (r'^Salidas/$', views.salidas_View),
    (r'^Salida/$', views.salida_manageView),
    (r'^Salida/(?P<id>\d+)/', views.salida_manageView),
    (r'^Salida/Delete/(?P<id>\d+)/', views.salida_delete),
    
)