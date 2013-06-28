import autocomplete_light

from models import *

autocomplete_light.register(ClavesArticulos, search_fields=('clave',),
    autocomplete_js_attributes={'placeholder': 'clave ..'})

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'nombre ..'})

