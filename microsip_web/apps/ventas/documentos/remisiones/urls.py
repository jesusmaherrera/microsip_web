from django.conf.urls import patterns
from .views import remisiones_view, remision_manageview

urlpatterns = patterns('',
	(r'^remisiones/$', remisiones_view),
	# (r'^remision/$', remision_manageview),
	(r'^remision/(?P<id>\d+)/$', remision_manageview),
)