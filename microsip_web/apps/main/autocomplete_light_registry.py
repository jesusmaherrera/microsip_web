from ...libs.api.models import *
from microsip_web.apps.main.filtros.models import *
from microsip_api.apps.config.models import Empresa
import autocomplete_light
from django.db.models import Q

autocomplete_light.register(
        Proveedor, 
        search_fields=('nombre',), 
        autocomplete_js_attributes={'placeholder': 'Busca un proveedor ..'}, 
        name='ProveedorAutocomplete'
    )

autocomplete_light.register(ArticuloClave, search_fields=('clave',),
    autocomplete_js_attributes={'placeholder': 'Clave ..'})

autocomplete_light.register(Articulo, autocomplete_js_attributes = {'placeholder':'Articulo'},
        search_fields = ('nombre',), choices= Articulo.objects.filter( Q(seguimiento='N') | Q(seguimiento='S'), estatus='A' ) )

autocomplete_light.register(
		Articulo, 
		autocomplete_js_attributes = {'placeholder':'Articulo'},
	    search_fields = ('nombre',), 
	    choices= Articulo.objects.filter( es_almacenable= 'N' ),
	    name='Articulos_noalm_Autocomplete',
    )

autocomplete_light.register(Cliente, autocomplete_js_attributes={'placeholder': 'Busca un cliente ..'}, 
        search_fields=('nombre',), choices= Cliente.objects.all(), name='ClienteAutocomplete')



autocomplete_light.register(Ciudad, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Ciudad ..'})

autocomplete_light.register(ContabilidadCuentaContable, search_fields=('cuenta','nombre',),
    autocomplete_js_attributes={'placeholder': 'Cuenta ..'})

autocomplete_light.register(Carpeta, search_fields=('nombre',))