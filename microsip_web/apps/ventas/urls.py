from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.ventas import views

urlpatterns = patterns('',
	(r'^Facturas/$', views.facturas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),
)