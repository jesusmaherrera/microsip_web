from django.conf.urls import patterns
from .views import generar_polizas_View, plantilla_poliza_manageView, plantilla_poliza_delete, preferenciasEmpresa_View

urlpatterns = patterns('',
	(r'^PreferenciasEmpresa/$', preferenciasEmpresa_View),
	(r'^GenerarPolizas/$', generar_polizas_View),
	#Plantilla Poliza
	(r'^plantilla_poliza/$', plantilla_poliza_manageView),
    (r'^plantilla_poliza/(?P<id>\d+)/', plantilla_poliza_manageView),
    (r'^plantilla_poliza/eliminar/(?P<id>\d+)/', plantilla_poliza_delete),
)