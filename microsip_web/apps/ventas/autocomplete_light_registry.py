import autocomplete_light

<<<<<<< HEAD
from microsip_web.apps.main.models import CuentaCo, Articulos
=======
from microsip_web.apps.inventarios.models import CuentaCo
>>>>>>> parent of ec0d228... se inicio con app filtros y compatibilidades

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'cuenta ..'},
    widget_js_attributes={'required':False,})
