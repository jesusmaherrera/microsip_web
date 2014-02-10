from django.conf.urls import patterns, url
from django.views import generic
import views

urlpatterns = patterns('',
	(r'^ordenes/$', views.ordenes_view),
	(r'^orden/$', views.orden_manageview),
	(r'^orden/(?P<id>\d+)/', views.orden_manageview),
    
)
