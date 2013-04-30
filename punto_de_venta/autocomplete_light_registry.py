import autocomplete_light

from inventarios.models import *

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'nombre ..'})

autocomplete_light.register(Cliente, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'busca un cliente ..'})