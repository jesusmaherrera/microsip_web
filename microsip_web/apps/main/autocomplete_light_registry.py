from models import *
from microsip_web.apps.main.filtros.models import *
import autocomplete_light

autocomplete_light.register(ClavesArticulos, search_fields=('clave',),
    autocomplete_js_attributes={'placeholder': 'Clave ..'})

class AutocompleteArticulos(autocomplete_light.AutocompleteModelBase):
	autocomplete_js_attributes = {'placeholder':'Articulo'}
	search_fields = ('nombre',)

	def choices_for_request(Self):
		self.request.GET.get('q','')
		articulo_id = self.request.GET.get('articulo_id', None)
		conexion_activa =  request.user.userprofile.conexion_activa
		choices = Articulos.objects.using(conexion_activa).all()

		if q:
			choices = choices.filter(nombre=q)
		if articulo_id:
			articulo_id = choices.filter(articulo_id=articulo_id)
		
		return self.order_choices(choice)[0:self.limit_choices]

autocomplete_light.register(Articulos, AutocompleteArticulos)

autocomplete_light.register(Ciudad, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Ciudad ..'})

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'Cuenta ..'})

autocomplete_light.register(Cliente, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Busca un cliente ..'})

autocomplete_light.register(Carpeta, search_fields=('nombre',))