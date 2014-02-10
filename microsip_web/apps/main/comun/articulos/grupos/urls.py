from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^grupos/$', views.grupos_lineas_view),
	(r'^grupo/(?P<id>\d+)/', views.grupo_lineas_manageView),
    (r'^grupo/', views.grupo_lineas_manageView),
)