from django.conf.urls import patterns
from .views import remisiones_view, generar_cargosbyremisionesview

urlpatterns = patterns('',
	(r'^remisiones/$', remisiones_view),
	(r'^generar_cargos/$', generar_cargosbyremisionesview.as_view()),
	# (r'^generar_cargo/$', generar_cargosbyremisionesview.as_view()),
)