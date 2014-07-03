from django.conf.urls import patterns, url
from django.views import generic
from views import *

urlpatterns = patterns('',
	(r'^generar_tarjetas/$', generar_tarjetas),
    (r'^inicializar_puntos_articulos/$', inicializar_puntos_articulos),
)