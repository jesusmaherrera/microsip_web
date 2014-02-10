from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^clientes/$', views.clientes_view),
	(r'^cliente/(?P<id>\d+)/', views.cliente_manageView),
    (r'^cliente/', views.cliente_manageView),
)