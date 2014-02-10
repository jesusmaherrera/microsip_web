from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^articulos/$', views.articulos_view),
	(r'^articulos/(?P<carpeta>\d+)/', views.articulos_view),
	(r'^articulo/(?P<id>\d+)/', views.articulo_manageview),
    (r'^articulo/', views.articulo_manageview),
)