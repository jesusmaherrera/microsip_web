import autocomplete_light

from microsip_web.apps.main.models import CuentaCo, Ciudad

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'cuenta ..'})

autocomplete_light.register(Ciudad, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Ciudad ..'})