from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^condiciones_de_pago/$', views.condiciones_de_pago_view),
	(r'^condicion_de_pago/(?P<id>\d+)/', views.condicion_de_pago_manageView),
 	(r'^condicion_de_pago/', views.condicion_de_pago_manageView),
)