from django.conf.urls import patterns, url
from django.views import generic
from microsip_web.apps.cuentas_por_pagar import views

urlpatterns = patterns('',
	#Proveedores
	# (r'^proveedor/$', views.proveedor_manageView),
 #    (r'^proveedor/(?P<id>\d+)/', views.proveedor_manageView),
	# (r'^proveedores/$', views.proveedores_view),
	# #Tipos Proveedores
	# (r'^tipos_proveedores/$', views.tipos_proveedores_view),
	(r'^GenerarPolizas/$', views.generar_polizas_View),
	(r'^PreferenciasEmpresa/$', views.preferenciasEmpresa_View),
	#Plantilla Poliza
	(r'^plantilla_poliza/$', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', views.plantilla_poliza_manageView),
    (r'^plantilla_poliza/eliminar/(?P<id>\d+)/', views.plantilla_poliza_delete),
)