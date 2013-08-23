from models import *
from microsip_web.apps.main.filtros.models import *
from microsip_web.apps.config.models import Empresa
from microsip_web.settings.common import MICROSIP_DATABASES
import autocomplete_light
import fdb

autocomplete_light.register(ClavesArticulos, search_fields=('clave',),
    autocomplete_js_attributes={'placeholder': 'Clave ..'})

autocomplete_light.register(Articulos, autocomplete_js_attributes = {'placeholder':'Articulo'},
        search_fields = ('nombre',), choices= Articulos.objects.using('VETERINARIA').all())

#Autocomplete para todas las empresas
# db= fdb.connect(host="localhost",user="SYSDBA",password="masterkey",database="C:\Microsip datos\System\CONFIG.FDB")
# cur = db.cursor()
# consulta = u"SELECT EMPRESAS.nombre_corto FROM EMPRESAS"
# cur.execute(consulta)
# empresas_rows = cur.fetchall()

for empresa in MICROSIP_DATABASES.keys():
    autocomplete_light.register(Articulos, autocomplete_js_attributes = {'placeholder':'Articulo'},
        search_fields=('nombre',), choices= Articulos.objects.using(empresa).all(), name='ArticulosAutocomplete-%s'%empresa)

    autocomplete_light.register(Cliente, autocomplete_js_attributes={'placeholder': 'Busca un cliente ..'}, 
        search_fields=('nombre',), choices= Cliente.objects.using(empresa).all(), name='ClienteAutocomplete-%s'%empresa)

autocomplete_light.register(Ciudad, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Ciudad ..'})

autocomplete_light.register(CuentaCo, search_fields=('cuenta',),
    autocomplete_js_attributes={'placeholder': 'Cuenta ..'})



autocomplete_light.register(Carpeta, search_fields=('nombre',))