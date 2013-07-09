from models import *
from microsip_web.apps.main.filtros.models import *
import autocomplete_light

autocomplete_light.register(ClavesArticulos, search_fields=('clave',),
    autocomplete_js_attributes={'placeholder': 'clave ..'})

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'nombre ..'})

autocomplete_light.register(Ciudad, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Ciudad ..'})

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'cuenta ..'})

autocomplete_light.register(Cliente, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'busca un cliente ..'})

autocomplete_light.register(Carpeta, search_fields=('nombre',))