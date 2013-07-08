import autocomplete_light

from microsip_web.apps.main.models import *

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'nombre ..'})

autocomplete_light.register(Cliente, search_fields=('nombre',),
<<<<<<< HEAD
    autocomplete_js_attributes={'placeholder': 'busca un cliente ..'})

autocomplete_light.register(SeccionArticulos, search_fields=('nombre',))
=======
    autocomplete_js_attributes={'placeholder': 'busca un cliente ..'})
>>>>>>> parent of ec0d228... se inicio con app filtros y compatibilidades
