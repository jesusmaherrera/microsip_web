from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^compras/$', views.compras_view),
	(r'^compra/$', views.compra_manageview),
    (r'^compra/(?P<type>[CO])/(?P<id>\d+)/', views.compra_manageview),
    (r'^compra/(?P<type>[CO])/(?P<id>\d+)/', views.compra_manageview),
)