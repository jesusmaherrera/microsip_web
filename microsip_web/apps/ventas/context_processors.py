from microsip_web.settings.local_settings import MICROSIP_MODULES
from django.conf import settings

def menu(request):
	context = {'menu_ventas':[],'menu_modulos':[],}
	if 'microsip_web.apps.ventas.documentos' in MICROSIP_MODULES:
		context['menu_ventas'].append({
			'name': 'Documentos',
			'icon_class':'icon-folder-close',
			'items':[
				{'name':'Facturas', 'url':'/ventas/facturas/', 'icon_class':'icon-file'},
				{'name':'Remisiones', 'url':'/ventas/remisiones/', 'icon_class':'icon-file'},
			]
		})

	if 'microsip_web.apps.main.comun.articulos' in MICROSIP_MODULES:
		context['menu_ventas'].append({
			'name':'Articulos',
			'icon_class':'icon-barcode',
			'items':[
				{'name':'Articulos', 'url':'/ventas/articulos/', 'icon_class':'icon-barcode'},
				{'name':'Lineas', 'url':'/ventas/lineas/', 'icon_class':'icon-tasks'},
				{'name':'Grupos', 'url':'/ventas/grupos/', 'icon_class':'icon-globe'},
			]	
		})

	if 'microsip_web.apps.main.comun.clientes' in MICROSIP_MODULES:
		context['menu_ventas'].append({
			'name':'Clientes',
			'icon_class':'icon-user',
			'items':[
				{'name':'Clientes', 'url':'/ventas/clientes/', 'icon_class':'icon-user'},
				{'name':'Condiciones de pago', 'url':'/ventas/condiciones_de_pago/', 'icon_class':'icon-calendar'},
			]
		})

	if 'microsip_web.apps.main.comun.listas' in MICROSIP_MODULES:
		context['menu_ventas'].append({
			'name':'Listas',
			'icon_class':'icon-list-alt',
			'items':[
				{'name':'Impuestos', 'url':'/ventas/impuestos/', 'icon_class':'icon-tag'},
			]
		})
	if 'microsip_web.apps.main.comun.otros' in MICROSIP_MODULES:	
		context['menu_ventas'].append({
			'name':'Otros',
			'icon_class':'icon-th',
			'items':[
				{'name':'Tipos de cambio', 'url':'/ventas/tipos_cambio/', 'icon_class':'icon-road'},
				{'name':'Ciudades', 'url':'/ventas/ciudades/', 'icon_class':'icon-road'},
				{'name':'Estados', 'url':'/ventas/estados/', 'icon_class':'icon-flag'},
				{'name':'Paises', 'url':'/ventas/paises/', 'icon_class':'icon-globe'},
			]
		})

	if 'microsip_web.apps.cuentas_por_cobrar'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Cuentas por cobrar', 'url':'/cuentas_por_cobrar/', 'icon_class':'msicon-cuentas_por_cobrar', },
		)
	if 'microsip_web.apps.inventarios'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Inventarios', 'url':'/inventarios/main/', 'icon_class':'msicon-inventarios',},
		)
	if 'microsip_web.apps.ventas'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Ventas', 'url':'/ventas/', 'icon_class':'msicon-ventas', },
		)
	if 'microsip_web.apps.cuentas_por_pagar'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Cuentas por pagar', 'url':'/cuentas_por_pagar/main/', 'icon_class':'msicon-cuentas_por_pagar',},
		)
	if 'microsip_web.apps.compras'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Compras', 'url':'/compras/main/', 'icon_class':'msicon-compras', },
		)
	if 'microsip_web.apps.punto_de_venta'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Punto de venta', 'url':'/punto_de_venta/main/', 'icon_class':'msicon-punto_de_venta', },
		)
	if 'microsip_web.apps.contabilidad'in settings.MICROSIP_MODULES:
		context['menu_modulos'].append(
			{'name':'Contabilidad', 'url':'/contabilidad/polizas_pendientes/', 'icon_class':'msicon-contabilidad', },
		)

	for item in context['menu_modulos']:
		if item['url'].replace('main/', '') in request.path:
			item['active']= True

	# context['menu_modulos'].append(
	# 	{'name':'Ventas', 'url':'/ventas/articulos/', 'icon_class':'msicon-ventas',},
	# )
	# context['menu_modulos'].append(
	# 	{'name':'Ventas', 'url':'/ventas/articulos/', 'icon_class':'msicon-ventas',},
	# )
	# context['menu_modulos'].append(
	# 	{'name':'Ventas', 'url':'/ventas/articulos/', 'icon_class':'msicon-ventas',},
	# )
	return context