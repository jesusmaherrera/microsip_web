from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^impuestos/$', views.impuestos_view),
	(r'^impuesto/$', views.impuesto_manageView),
    (r'^impuesto/(?P<id>\d+)/', views.impuesto_manageView),
)