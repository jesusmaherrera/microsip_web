import autocomplete_light

from microsip_web.apps.inventarios.models import CuentaCo, Articulos

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'cuenta ..'},
    widget_js_attributes={'required':False,})

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'nombre ..'})