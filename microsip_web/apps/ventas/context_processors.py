from microsip_web.settings.local_settings import MICROSIP_MODULES

def menu(request):
	context = {'menu':[]}
	if 'microsip_web.apps.ventas.documentos' in MICROSIP_MODULES:
		context['menu'].append({
			'name': 'Documentos',
			'icon_class':'icon-folder-close',
			'items':[
				{'name':'Facturas', 'url':'/ventas/facturas/', 'icon_class':'icon-file'},
				{'name':'Remisiones', 'url':'/ventas/remisiones/', 'icon_class':'icon-file'},
			]
		})

	if 'microsip_web.apps.main.comun.articulos' in MICROSIP_MODULES:
		context['menu'].append({
			'name':'Articulos',
			'icon_class':'icon-barcode',
			'items':[
				{'name':'Articulos', 'url':'/ventas/articulos/', 'icon_class':'icon-barcode'},
				{'name':'Lineas', 'url':'/ventas/lineas/', 'icon_class':'icon-tasks'},
				{'name':'Grupos', 'url':'/ventas/grupos/', 'icon_class':'icon-globe'},
			]	
		})

	if 'microsip_web.apps.main.comun.clientes' in MICROSIP_MODULES:
		context['menu'].append({
			'name':'Clientes',
			'icon_class':'icon-user',
			'items':[
				{'name':'Clientes', 'url':'/ventas/clientes/', 'icon_class':'icon-user'},
				{'name':'Condiciones de pago', 'url':'/ventas/condiciones_de_pago/', 'icon_class':'icon-calendar'},
			]
		})

	if 'microsip_web.apps.main.comun.listas' in MICROSIP_MODULES:
		context['menu'].append({
			'name':'Listas',
			'icon_class':'icon-list-alt',
			'items':[
				{'name':'Impuestos', 'url':'/ventas/impuestos/', 'icon_class':'icon-tag'},
			]
		})
	if 'microsip_web.apps.main.comun.otros' in MICROSIP_MODULES:	
		context['menu'].append({
			'name':'Otros',
			'icon_class':'icon-th',
			'items':[
				{'name':'Tipos de cambio', 'url':'/ventas/tipos_cambio/', 'icon_class':'icon-road'},
				{'name':'Ciudades', 'url':'/ventas/ciudades/', 'icon_class':'icon-road'},
				{'name':'Estados', 'url':'/ventas/estados/', 'icon_class':'icon-flag'},
				{'name':'Paises', 'url':'/ventas/paises/', 'icon_class':'icon-globe'},
			]
		})
	return context