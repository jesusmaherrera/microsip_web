#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *

from cuentas_por_pagar.forms import *
from main.views import get_folio_poliza
import json
from decimal import *

import datetime, time
from django.db.models import Q
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from django.db import connection
from inventarios.views import c_get_next_key
import ventas 

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa_CP.html'):
	try:
		informacion_contable = InformacionContable_CP.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_CP()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	plantillas = PlantillaPolizas_CP.objects.all()
	c= {'form':form,'msg':msg,'plantillas':plantillas,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

def get_totales_cuentas_by_segmento(segmento='',totales_cuentas=[], depto_co=None, concepto_tipo=None, error=0, msg='', documento_folio='', asiento_ingora=0):
	importe = 0
	cuenta 	= []
	clave_cuenta_tipoAsiento = []

	segmento = segmento.split(',')
	
	if not segmento == []:
		for importe_segmento in segmento:

			cuenta_cantidad 	= importe_segmento.split('=')
			cuenta_depto= cuenta_cantidad[0].split("/")

			try:
				cuenta 		=  CuentaCo.objects.get(cuenta=cuenta_depto[0]).cuenta
			except ObjectDoesNotExist:
				error = 2
				msg = 'NO EXISTE almenos una [CUENTA CONTABLE] indicada en un segmento en el documento con folio[%s], Corrigelo para continuar'% documento_folio
			
			if len(cuenta_depto) == 2:
				try:
					depto = DeptoCo.objects.get(clave=cuenta_depto[1]).clave
				except ObjectDoesNotExist:
					error = 2
					msg = 'NO EXISTE almenos un [DEPARTEMENTO CONTABLE] indicado en un segmento en el documento con folio [%s], Corrigelo para continuar'% documento_folio
			else:
				depto = depto_co

			try:
				importe = float(cuenta_cantidad[1])
			except:
				error = 3
				msg = 'Cantidad incorrecta en un segmento en el documento [%s], Corrigelo para continuar'% documento_folio

			if error == 0:
				clave_cuenta_tipoAsiento = "%s/%s:%s"% (cuenta, depto, concepto_tipo)
				importe = importe

				if not clave_cuenta_tipoAsiento == [] and importe > 0:
					if clave_cuenta_tipoAsiento in totales_cuentas:
						totales_cuentas[clave_cuenta_tipoAsiento] = [totales_cuentas[clave_cuenta_tipoAsiento][0] + Decimal(importe),int(asiento_ingora)]
					else:
						totales_cuentas[clave_cuenta_tipoAsiento]  = [Decimal(importe),int(asiento_ingora)]
	return totales_cuentas, error, msg

def get_totales_documento_cuentas(cuenta_contado = None, documento=None, conceptos_poliza=None, totales_cuentas=None, msg='', error='',depto_co=None):
	campos_particulares = LibresCargosCP.objects.filter(pk=documento.id)[0]
	try:
		cuenta_proveedor =  CuentaCo.objects.get(cuenta=documento.proveedor.cuenta_xpagar).cuenta
	except ObjectDoesNotExist:
		cuenta_proveedor = None
		error = 1
		msg ='no se encontro el proveedor'

	#Para saber si es contado o es credito
	if documento.naturaleza_concepto == 'C':
		es_contado = documento.condicion_pago == cuenta_contado
	else:
		es_contado = False

	importesDocto 		= ImportesDoctosCP.objects.filter(docto_cp=documento)[0]
	
	impuestos 			= importesDocto.total_impuestos * documento.tipo_cambio
	importe_neto 		= importesDocto.importe_neto * documento.tipo_cambio
	total 				= impuestos + importe_neto
	descuento 			= 0
	proveedores 		= 0
	bancos 				= 0
	compras_0 			= 0
	compras_16      	= 0
	compras_16_credito 	= 0
	compras_0_credito	= 0
	compras_16_contado 	= 0
	compras_0_contado	= 0
	iva_pend_pagar 		= 0
	iva_efec_pagado 	= 0
	iva_retenido		= importesDocto.iva_retenido

	if impuestos <= 0:
		compras_0 = importe_neto
	else:
		compras_16 = importe_neto

	#si llega a  haber un proveedor que no tenga cargar impuestos
	if compras_16 < 0:
		compras_0 += compras_16
		compras_16 = 0
		msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
		if crear_polizas_por == 'Dia':
			msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

		error = 1

	#Si es a credito
	if not es_contado:
		compras_16_credito 	= compras_16
		compras_0_credito 	= compras_0
		iva_pend_pagar 		= impuestos
		proveedores 		= total - descuento
	elif es_contado:
		compras_16_contado 	= compras_16
		compras_0_contado	= compras_0
		iva_efec_pagado 	= impuestos
		bancos 				= total - descuento

	asientos_a_ingorar = []
	for concepto in conceptos_poliza:
		if concepto.valor_tipo == 'Segmento_1' and not campos_particulares.segmento_1 == None:
			asientos_a_ingorar.append(concepto.asiento_ingora)
		if concepto.valor_tipo == 'Segmento_2' and not campos_particulares.segmento_2 == None:
			asientos_a_ingorar.append(concepto.asiento_ingora)
		if concepto.valor_tipo == 'Segmento_3' and not campos_particulares.segmento_3 == None:
			asientos_a_ingorar.append(concepto.asiento_ingora)
		if concepto.valor_tipo == 'Segmento_4' and not campos_particulares.segmento_4 == None:
			asientos_a_ingorar.append(concepto.asiento_ingora)
		if concepto.valor_tipo == 'Segmento_5' and not campos_particulares.segmento_5 == None:
			asientos_a_ingorar.append(concepto.asiento_ingora)

	for concepto in conceptos_poliza:
		importe = 0
		cuenta 	= []
		clave_cuenta_tipoAsiento = []
		
		if concepto.valor_tipo == 'Segmento_1' and not campos_particulares.segmento_1 == None:
			totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_1, totales_cuentas, depto_co, concepto.tipo, error, msg, documento.folio, concepto.asiento_ingora)
		elif concepto.valor_tipo == 'Segmento_2' and not campos_particulares.segmento_2 == None: 
			totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_2, totales_cuentas, depto_co, concepto.tipo, error, msg, documento.folio, concepto.asiento_ingora)
		elif concepto.valor_tipo == 'Segmento_3' and not campos_particulares.segmento_3 == None: 
			totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_3, totales_cuentas, depto_co, concepto.tipo, error, msg, documento.folio, concepto.asiento_ingora)
		elif concepto.valor_tipo == 'Segmento_4' and not campos_particulares.segmento_4 == None:
			totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_4, totales_cuentas, depto_co, concepto.tipo, error, msg, documento.folio, concepto.asiento_ingora)
		elif concepto.valor_tipo == 'Segmento_5' and not campos_particulares.segmento_5 == None: 
			totales_cuentas, error, msg = get_totales_cuentas_by_segmento(campos_particulares.segmento_5, totales_cuentas, depto_co, concepto.tipo, error, msg, documento.folio, concepto.asiento_ingora)
		elif concepto.valor_tipo == 'Compras' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_contado_credito == 'Credito':
				if concepto.valor_iva == '0':
					importe = compras_0_credito
				elif concepto.valor_iva == 'I':
					importe = compras_16_credito
				elif concepto.valor_iva == 'A':
					importe = compras_0_credito + compras_16_credito
			elif concepto.valor_contado_credito == 'Contado':
				if concepto.valor_iva == '0':
					importe = compras_0_contado
				elif concepto.valor_iva == 'I':
					importe = compras_16_contado
				elif concepto.valor_iva == 'A':
					importe = compras_0_contado + compras_16_contado
			elif concepto.valor_contado_credito == 'Ambos':
				if concepto.valor_iva == '0':
					importe = compras_0_credito + compras_0_contado
				elif concepto.valor_iva == 'I':
					importe = compras_16_credito + compras_16_contado
				elif concepto.valor_iva == 'A':
					importe = compras_0_credito + compras_0_contado + compras_16_credito + compras_16_contado
			cuenta  = concepto.cuenta_co.cuenta

		elif concepto.valor_tipo == 'IVA' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_contado_credito == 'Credito':
				importe = iva_pend_pagar
			elif concepto.valor_contado_credito == 'Contado':
				importe = iva_efec_pagado
			elif concepto.valor_contado_credito == 'Ambos':
				importe = iva_pend_pagar + iva_efec_pagado

			cuenta = concepto.cuenta_co.cuenta

		elif concepto.valor_tipo == 'IVA Retenido' and not concepto.posicion in asientos_a_ingorar:
			importe = iva_retenido
			cuenta = concepto.cuenta_co.cuenta
						
		elif concepto.valor_tipo == 'Proveedores' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_iva == 'A':
				importe = proveedores

			if cuenta_proveedor == None:
				cuenta = concepto.cuenta_co.cuenta
			else:
				cuenta = cuenta_proveedor

		elif concepto.valor_tipo == 'Bancos' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_iva == 'A':
				importe =	bancos

			cuenta = concepto.cuenta_co.cuenta

		elif concepto.valor_tipo == 'Descuentos' and not concepto.posicion in asientos_a_ingorar:
			importe = descuento
			cuenta = concepto.cuenta_co.cuenta

		clave_cuenta_tipoAsiento = "%s/%s:%s"% (cuenta, depto_co, concepto.tipo)
		importe = importe

		#Se es tipo segmento pone variables en cero para que no se calculen otra ves valores por ya estan calculados
		if concepto.valor_tipo == 'Segmento_1' or concepto.valor_tipo == 'Segmento_2' or concepto.valor_tipo == 'Segmento_3' or concepto.valor_tipo == 'Segmento_4' or concepto.valor_tipo == 'Segmento_5':
			importe = 0

		if not clave_cuenta_tipoAsiento == [] and importe > 0:
			if clave_cuenta_tipoAsiento in totales_cuentas:
				totales_cuentas[clave_cuenta_tipoAsiento] = [totales_cuentas[clave_cuenta_tipoAsiento][0] + Decimal(importe),int(concepto.posicion)]
			else:
				totales_cuentas[clave_cuenta_tipoAsiento]  = [Decimal(importe),int(concepto.posicion)]

	return totales_cuentas, error, msg

def crear_polizas(documentos, depto_co, informacion_contable, msg, plantilla=None, descripcion = '', crear_polizas_por='',crear_polizas_de=None,):
	error = 0
	DocumentosData 		= []
	cuenta 				= ''
	importe = 0
	conceptos_poliza	= DetallePlantillaPolizas_CP.objects.filter(plantilla_poliza_CP=plantilla).order_by('posicion')
	moneda_local 		= get_object_or_404(Moneda,es_moneda_local='S')
	documento_numero 	= 0
	polizas 			= []
	detalles_polizas 	= []
	totales_cuentas 	= {}
	
	for documento_no, documento in enumerate(documentos):
		if documento.naturaleza_concepto == 'C':
			es_contado = documento.condicion_pago == informacion_contable.condicion_pago_contado
		else:
			es_contado = False

		siguente_documento = documentos[(documento_no +1)%len(documentos)]
		documento_numero = documento_no
		
		totales_cuentas, error, msg = get_totales_documento_cuentas(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co)
		
		if error == 0:
			#Cuando la fecha de la documento siguiente sea diferente y sea por DIA, o sea la ultima
			if (not documento.fecha == siguente_documento.fecha and crear_polizas_por == 'Dia') or documento_no +1 == len(documentos) or crear_polizas_por == 'Documento':

				tipo_poliza = TipoPoliza.objects.filter(clave=documento.concepto.clave_tipo_poliza)[0]
				tipo_poliza_det = get_folio_poliza(tipo_poliza, documento.fecha)
				#PREFIJO
				prefijo = tipo_poliza.prefijo
				if not tipo_poliza.prefijo:
					prefijo = ''

				#Si no tiene una descripcion el documento se pone lo que esta indicado en la descripcion general
				descripcion_doc = documento.descripcion
				
				if documento.descripcion == None or crear_polizas_por=='Dia' or crear_polizas_por == 'Periodo':
					descripcion_doc = descripcion

				referencia = documento.folio
				
				if crear_polizas_por == 'Dia':
					referencia = ''

				poliza = DoctoCo(
						id                    	= c_get_next_key('ID_DOCTOS'),
						tipo_poliza				= tipo_poliza,
						poliza					= '%s%s'% (prefijo,("%09d" % tipo_poliza_det.consecutivo)[len(prefijo):]),
						fecha 					= documento.fecha,
						moneda 					= moneda_local, 
						tipo_cambio 			= 1,
						estatus 				= 'P', cancelado= 'N', aplicado = 'N', ajuste = 'N', integ_co = 'S',
						descripcion 			= descripcion_doc,
						forma_emitida 			= 'N', sistema_origen = 'CO',
						nombre 					= '',
						grupo_poliza_periodo 	= None,
						integ_ba 				= 'N',
						usuario_creador			= 'SYSDBA',
						fechahora_creacion		= datetime.datetime.now(), usuario_aut_creacion = None, 
						usuario_ult_modif 		= 'SYSDBA', fechahora_ult_modif = datetime.datetime.now(), usuario_aut_modif 	= None,
						usuario_cancelacion 	= None, fechahora_cancelacion 	=  None, usuario_aut_cancelacion 				= None,
					)
				
				polizas.append(poliza)
				#GUARDA LA PILIZA
				#poliza_o = poliza.save()

				#CONSECUTIVO DE FOLIO DE POLIZA
				tipo_poliza_det.consecutivo += 1 
				tipo_poliza_det.save()

				posicion = 1
				totales_cuentas = totales_cuentas.items()


				for cuenta_depto_tipoAsiento, importe in totales_cuentas:
					cuenta_deptotipoAsiento = cuenta_depto_tipoAsiento.split('/')
					cuenta_co = CuentaCo.objects.get(cuenta=cuenta_deptotipoAsiento[0])
					depto_tipoAsiento = cuenta_deptotipoAsiento[1].split(':')
					depto_co = DeptoCo.objects.get(clave=depto_tipoAsiento[0])
					tipo_asiento = depto_tipoAsiento[1]

					detalle_poliza = DoctosCoDet(
						id				= -1,
						docto_co		= poliza,
						cuenta			= cuenta_co,
						depto_co		= depto_co,
						tipo_asiento	= tipo_asiento,
						importe			= importe[0],
						importe_mn		= 0,#PENDIENTE
						ref				= referencia,
						descripcion		= '',
						posicion		= posicion,
						recordatorio	= None,
						fecha			= documento.fecha,
						cancelado		= 'N', aplicado = 'N', ajuste = 'N', 
						moneda			= moneda_local,
					)

					posicion +=1
					detalles_polizas.append(detalle_poliza)

				#DE NUEVO COMBIERTO LA VARIABLE A DICCIONARIO
				totales_cuentas = {}

				DocumentosData.append ({
					'folio'		:poliza.poliza,
					})

 			DoctosCp.objects.filter(id=documento.id).update(contabilizado = 'S')
 	
 	if error == 0:
		DoctoCo.objects.bulk_create(polizas)
		DoctosCoDet.objects.bulk_create(detalles_polizas)
	else:
		DocumentosData = []

	polizas = []
	detalles_polizas = []
	return msg, DocumentosData

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_documentos_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla='', descripcion= ''):
	
	error 	= 0
	msg		= ''
	documentosCPData = []
	
	try:
		informacion_contable = InformacionContable_CP.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1

	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		if ignorar_documentos_cont:
			documentosCP  = DoctosCp.objects.filter(contabilizado ='N', concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			documentosCP  = DoctosCp.objects.filter(concepto= crear_polizas_de , fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]

		msg, documentosCPData = crear_polizas(documentosCP, informacion_contable.depto_general_cont , informacion_contable, msg , plantilla, descripcion, crear_polizas_por, crear_polizas_de)
	
	elif error == 1 and msg=='':
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'

	return documentosCPData, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='herramientas/generar_polizas_CP.html'):
	
	documentosData 	= []
	msg 			= msg_resultados = ''

	if request.method == 'POST':
		
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():
			fecha_ini 				= form.cleaned_data['fecha_ini']
			fecha_fin 				= form.cleaned_data['fecha_fin']
			ignorar_documentos_cont = form.cleaned_data['ignorar_documentos_cont']
			crear_polizas_por 		= form.cleaned_data['crear_polizas_por']
			crear_polizas_de 		= form.cleaned_data['crear_polizas_de']
			plantilla 				= form.cleaned_data['plantilla']
			descripcion 			= form.cleaned_data['descripcion']

			msg = 'es valido'

			documentosData, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_documentos_cont, crear_polizas_por, crear_polizas_de, plantilla, descripcion)
			if documentosData == []:
				msg_resultados = 'Lo siento, no se encontraron resultados para este filtro'
	else:
		form = GenerarPolizasManageForm()

	c = {'documentos':documentosData,'msg':msg,'form':form, 'msg_resultados':msg_resultados,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='herramientas/plantilla_poliza_CP.html'):
	message = ''

	if id:
		plantilla = get_object_or_404(PlantillaPolizas_CP, pk=id)
	else:
		plantilla =PlantillaPolizas_CP()

	if request.method == 'POST':
		plantilla_form = PlantillaPolizaManageForm(request.POST, request.FILES, instance=plantilla)

		plantilla_items 		= PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_items_formset = plantilla_items(request.POST, request.FILES, instance=plantilla)
		
		if plantilla_form.is_valid() and plantilla_items_formset .is_valid():
			plantilla = plantilla_form.save(commit = False)
			plantilla.save()

			#GUARDA CONCEPTOS DE PLANTILLA
			for concepto_form in plantilla_items_formset :
				Detalleplantilla = concepto_form.save(commit = False)
				#PARA CREAR UNO NUEVO
				if not Detalleplantilla.id:
					Detalleplantilla.plantilla_poliza_CP = plantilla
			
			plantilla_items_formset.save()
			return HttpResponseRedirect('/cuentas_por_pagar/PreferenciasEmpresa/')
	else:
		plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_form= PlantillaPolizaManageForm(instance=plantilla)
	 	plantilla_items_formset  = plantilla_items(instance=plantilla)
	
	c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_delete(request, id = None):
	plantilla = get_object_or_404(PlantillaPolizas_CP, pk=id)
	plantilla.delete()

	return HttpResponseRedirect('/cuentas_por_pagar/PreferenciasEmpresa/')


@login_required(login_url='/login/')
def proveedores_view(request, template_name='catalogos/proveedores/proveedores.html'):
	provedores_list = Proveedor.objects.all()

	paginator = Paginator(provedores_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		proveedores = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    proveedores = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    proveedores = paginator.page(paginator.num_pages)

	c = {'proveedores':proveedores}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def proveedor_manageView(request, id = None, template_name='catalogos/proveedores/proveedor.html'):
	message = ''

	if id:
		proveedor = get_object_or_404(Proveedor, pk=id)
	else:
		proveedor = Proveedor()

	if request.method == 'POST':
		form = ProveedorManageForm(request.POST, instance= proveedor)
	else:
		form = ProveedorManageForm(instance=proveedor)

	c = {'form':form}
	return render_to_response(template_name, c, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def tipos_proveedores_view(request, template_name='catalogos/tipos_proveedores/tipos_proveedores.html'):
	tipos_provedores_list = TipoProveedor.objects.all()

	paginator = Paginator(tipos_provedores_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		tipos_proveedores = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    tipos_proveedores = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    tipos_proveedores = paginator.page(paginator.num_pages)

	c = {'tipos_proveedores':tipos_proveedores}
	return render_to_response(template_name, c, context_instance=RequestContext(request))