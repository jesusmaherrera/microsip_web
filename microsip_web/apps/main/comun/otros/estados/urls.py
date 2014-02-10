from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^estados/$', views.estados_view),
	(r'^estado/$', views.estado_manageView),
 	(r'^estado/(?P<id>\d+)/', views.estado_manageView),
)