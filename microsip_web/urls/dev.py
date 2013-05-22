
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views import generic
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

dajaxice_autodiscover()
import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
	#main
    url(r'', include('microsip_web.apps.main.urls', namespace='main')),
    #Descomentar esta linea para habilitar inventarios
    url(r'^inventarios/', include('microsip_web.apps.inventarios.urls', namespace='Inventarios')),

    #Descomentar esta linea para habilitar ventas
    url(r'^ventas/', include('microsip_web.apps.ventas.urls', namespace='ventas')),

    #Descomentar esta linea para habilitar cuentas_por_cobrar
    url(r'^cuentas_por_cobrar/', include('microsip_web.apps.cuentas_por_cobrar.urls', namespace='cuentas_por_cobrar')),

    #Descomentar esta linea para habilitar cuentas_por_pagar
    url(r'^cuentas_por_pagar/', include('microsip_web.apps.cuentas_por_pagar.urls', namespace='cuentas_por_pagar')),
    
    #Descomentar esta linea para habilitar punto_de_venta
    url(r'^punto_de_venta/', include('microsip_web.apps.punto_de_venta.urls', namespace='punto_de_venta')),

    #Descomentar esta linea para habilitar contabilidad
    url(r'^contabilidad/', include('microsip_web.apps.contabilidad.urls', namespace='contabilidad')),
    
    url(r'autocomplete/', include('autocomplete_light.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #LOGIN
    url(r'^login/$','microsip_web.apps.inventarios.views.ingresar'),
    url(r'^logout/$', 'microsip_web.apps.inventarios.views.logoutUser'),
)

urlpatterns += staticfiles_urlpatterns()