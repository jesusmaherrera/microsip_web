from django.conf.urls import patterns
from .views import remisiones_view

urlpatterns = patterns('',
	(r'^remisiones/$', remisiones_view),
)