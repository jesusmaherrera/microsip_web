from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^tipos_cambio/$', views.tipos_cambio_view),
)