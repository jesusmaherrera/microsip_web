from django.conf.urls import patterns, url
from django.views import generic
from punto_de_venta import views

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
)