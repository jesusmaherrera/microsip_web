from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.contabilidad import views

urlpatterns = patterns('',
	 (r'^polizas/$', views.polizas_View),
	 (r'^polizas_pendientes/$', views.polizas_pendientesView),
	 (r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	 #(r'^generar_diot/$', views.generar_diotView),
)