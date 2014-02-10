from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^ciudades/$', views.ciudades_view),
	(r'^ciudad/$', views.ciudad_manageView),
 	(r'^ciudad/(?P<id>\d+)/', views.ciudad_manageView),
)