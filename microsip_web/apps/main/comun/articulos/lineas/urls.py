from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^lineas/$', views.lineas_articulos_view),
	(r'^linea/(?P<id>\d+)/', views.linea_articulos_manageView),
    (r'^linea/', views.linea_articulos_manageView),
)