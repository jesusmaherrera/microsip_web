from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^paises/$', views.paises_view),
	(r'^pais/$', views.pais_manageView),
    (r'^pais/(?P<id>\d+)/', views.pais_manageView),
)