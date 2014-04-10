from django.conf.urls import patterns
from .views import generar_cargosbyremisionesview, VentasDocumentoRemisionesListView

urlpatterns = patterns('',
	(r'^remisiones/$', VentasDocumentoRemisionesListView.as_view()),
	(r'^generar_cargos/$', generar_cargosbyremisionesview.as_view()),
)