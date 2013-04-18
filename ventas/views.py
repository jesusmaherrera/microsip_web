#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from inventarios.models import *
from models import *
from forms import *
import datetime, time
from django.db.models import Q
from datetime import timedelta
from decimal import *
from cuentas_por_pagar.views import get_totales_cuentas_by_segmento
from django.core import serializers
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max
from django.db import connection
from inventarios.views import c_get_next_key
from main.views import get_folio_poliza

##########################################
## 										##
##              POLIZAS           	    ##
##										##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa.html'):
	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_V()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	plantillas = PlantillaPolizas_V.objects.all()

	c= {'form':form,'msg':msg,'plantillas':plantillas,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

def get_descuento_total_ve(facturaID):
	c = connection.cursor()
	c.execute("SELECT SUM(A.dscto_arts + A.dscto_extra_importe) AS TOTAL FROM CALC_TOTALES_DOCTO_VE(%s,'S') AS  A;"% facturaID)
	row = c.fetchone()
	return int(row[0])

def get_totales_doctos_ve(cuenta_contado= None, documento= None, conceptos_poliza=None, totales_cuentas=None, msg='', error='', depto_co=None):	
	#Si es una factura
	if documento.tipo == 'F':
		campos_particulares = LibresFacturasV.objects.filter(pk=documento.id)[0]
	#Si es una devolucion
	elif documento.tipo == 'D':
		campos_particulares = LibresDevFacV.objects.filter(pk=documento.id)[0]

	try:
		cuenta_cliente =  CuentaCo.objects.get(cuenta=documento.cliente.cuenta_xcobrar).cuenta
	except ObjectDoesNotExist:
		cuenta_cliente = None

	#Para saber si es contado o es credito
	es_contado = documento.condicion_pago == cuenta_contado

	impuestos 			= documento.total_impuestos * documento.tipo_cambio
	importe_neto 		= documento.importe_neto * documento.tipo_cambio
	total 				= impuestos + importe_neto
	descuento 			= get_descuento_total_ve(documento.id) * documento.tipo_cambio
	clientes 			= total - descuento
	bancos 				= 0
	iva_efec_cobrado	= 0
	iva_pend_cobrar 	= 0
	ventas_16_credito	= 0
	ventas_16_contado	= 0
	ventas_0_credito	= 0
	ventas_0_contado	= 0

	ventas_0 			= DoctoVeDet.objects.filter(docto_ve= documento).extra(
			tables =['impuestos_articulos', 'impuestos'],
			where =
			[
				"impuestos_articulos.ARTICULO_ID = doctos_ve_det.ARTICULO_ID",
				"impuestos.IMPUESTO_ID = impuestos_articulos.IMPUESTO_ID",
				"impuestos.PCTJE_IMPUESTO = 0 ",
			],
		).aggregate(ventas_0 = Sum('precio_total_neto'))['ventas_0']
	
	if ventas_0 == None:
		ventas_0 = 0 

	ventas_0 = ventas_0 * documento.tipo_cambio

	ventas_16 = total - ventas_0 - impuestos

	#si llega a  haber un proveedor que no tenga cargar impuestos
	if ventas_16 < 0:
		ventas_0 += ventas_16
		ventas_16 = 0
		msg = 'Existe al menos una documento donde el proveedor [no tiene indicado cargar inpuestos] POR FAVOR REVISTA ESO!!'
		if crear_polizas_por == 'Dia':
			msg = '%s, REVISA LAS POLIZAS QUE SE CREARON'% msg 

		error = 1

	#SI LA FACTURA ES A CREDITO
	if not es_contado:
		ventas_16_credito 	= ventas_16
		ventas_0_credito 	= ventas_0
		iva_pend_cobrar 	= impuestos
		clientes 			= total - descuento
	elif es_contado:
		ventas_16_contado 	= ventas_16
		ventas_0_contado	= ventas_0
		iva_efec_cobrado 	= impuestos
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
		elif concepto.valor_tipo == 'Ventas' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_contado_credito == 'Credito':
				if concepto.valor_iva == '0':
					importe = ventas_0_credito
				elif concepto.valor_iva == 'I':
					importe = ventas_16_credito
				elif concepto.valor_iva == 'A':
					importe = ventas_0_credito + ventas_16_credito
			elif concepto.valor_contado_credito == 'Contado':
				if concepto.valor_iva == '0':
					importe = ventas_0_contado
				elif concepto.valor_iva == 'I':
					importe = ventas_16_contado
				elif concepto.valor_iva == 'A':
					importe = ventas_0_contado + ventas_16_contado
			elif concepto.valor_contado_credito == 'Ambos':
				if concepto.valor_iva == '0':
					importe = ventas_0_credito + ventas_0_contado
				elif concepto.valor_iva == 'I':
					importe = ventas_16_credito + ventas_16_contado
				elif concepto.valor_iva == 'A':
					importe = ventas_0_credito + ventas_0_contado + ventas_16_credito + ventas_16_contado
			cuenta  = concepto.cuenta_co.cuenta

		elif concepto.valor_tipo == 'IVA' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_contado_credito == 'Credito':
				importe = iva_pend_cobrar
			elif concepto.valor_contado_credito == 'Contado':
				importe = iva_efec_cobrado
			elif concepto.valor_contado_credito == 'Ambos':
				importe = iva_pend_cobrar + iva_efec_cobrado

			cuenta = concepto.cuenta_co.cuenta

		elif concepto.valor_tipo == 'Clientes' and not concepto.posicion in asientos_a_ingorar:
			if concepto.valor_iva == 'A':
				importe = clientes

			if cuenta_cliente == None:
				cuenta = concepto.cuenta_co.cuenta
			else:
				cuenta = cuenta_cliente

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

def crear_polizas(documentos, depto_co, informacion_contable, msg, plantilla=None, descripcion = '', crear_polizas_por='',crear_polizas_de=None, tipo_poliza=''):
	
	error = 0
	DocumentosData 		= []
	cuenta 				= ''
	importe = 0
	conceptos_poliza	= DetallePlantillaPolizas_V.objects.filter(plantilla_poliza_v=plantilla).order_by('posicion')
	moneda_local 		= get_object_or_404(Moneda,es_moneda_local='S')
	documento_numero 	= 0
	polizas 			= []
	detalles_polizas 	= []
	totales_cuentas 	= {}

	for documento_no, documento in enumerate(documentos):
		
		es_contado = documento.condicion_pago == informacion_contable.condicion_pago_contado
		
		siguente_documento = documentos[(documento_no +1)%len(documentos)]
		documento_numero = documento_no

		totales_cuentas, error, msg = get_totales_doctos_ve(informacion_contable.condicion_pago_contado, documento, conceptos_poliza, totales_cuentas, msg, error, depto_co)
		
		if error == 0:

			#Cuando la fecha de la documento siguiente sea diferente y sea por DIA, o sea la ultima
			if (not documento.fecha == siguente_documento.fecha and crear_polizas_por == 'Dia') or documento_no +1 == len(documentos) or crear_polizas_por == 'Documento':

				if 	tipo_poliza == 'F':
					tipo_poliza = informacion_contable.tipo_poliza_ve
				elif tipo_poliza == 'D': 
					tipo_poliza = informacion_contable.tipo_poliza_dev

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

			DoctoVe.objects.filter(id=documento.id).update(contabilizado = 'S')
	if error == 0:
		DoctoCo.objects.bulk_create(polizas)
		DoctosCoDet.objects.bulk_create(detalles_polizas)
	else:
		DocumentosData = []

	polizas = []
	detalles_polizas = []
	return DocumentosData, msg

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_documentos_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla_facturas='', plantilla_devoluciones='', descripcion= ''):
	error 	= 0
	msg		= ''
	documentosData = []
	documentosGenerados = []
	documentosDataDevoluciones = []
	
	try:
		informacion_contable = InformacionContable_V.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		facturas 	= []
		devoluciones= []
		if ignorar_documentos_cont:
			if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
				facturas 			= DoctoVe.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
				devoluciones 		= DoctoVe.objects.filter(estado = 'N').filter(tipo 	='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
				facturas 			= DoctoVe.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='F', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
				devoluciones 		= DoctoVe.objects.filter(estado = 'N').filter(tipo 	= 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		
		#PREFIJO
		prefijo = informacion_contable.tipo_poliza_ve.prefijo
		if not informacion_contable.tipo_poliza_ve.prefijo:
			prefijo = ''

		if crear_polizas_de 	== 'F' or crear_polizas_de 	== 'FD':
			documentosData, msg = crear_polizas(facturas, informacion_contable.depto_general_cont, informacion_contable, msg, plantilla_facturas, descripcion, crear_polizas_por, crear_polizas_de, 'F')
			documentosGenerados = documentosData
		if crear_polizas_de 	== 'D' or crear_polizas_de 	== 'FD':
			documentosDataDevoluciones, msg = crear_polizas(devoluciones, informacion_contable.depto_general_cont, informacion_contable, msg, plantilla_devoluciones, descripcion, crear_polizas_por, crear_polizas_de, 'D')

	elif error == 1 and msg=='':
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'
	
	return documentosGenerados, documentosDataDevoluciones, msg

@login_required(login_url='/login/')
def facturas_View(request, template_name='herramientas/generar_polizas.html'):
	documentosData = []
	polizas_de_devoluciones = []
	msg 			= ''

	if request.method == 'POST':
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():

			fecha_ini 				= form.cleaned_data['fecha_ini']
			fecha_fin 				= form.cleaned_data['fecha_fin']
			ignorar_documentos_cont = form.cleaned_data['ignorar_documentos_cont']
			crear_polizas_por 		= form.cleaned_data['crear_polizas_por']
			crear_polizas_de 		= form.cleaned_data['crear_polizas_de']
			plantilla_facturas 		= form.cleaned_data['plantilla']
			plantilla_devoluciones 	= form.cleaned_data['plantilla_2']
			descripcion 			= form.cleaned_data['descripcion']
			if (crear_polizas_de == 'F' and not plantilla_facturas== None) or (crear_polizas_de == 'D' and not plantilla_devoluciones== None) or (crear_polizas_de == 'FD' and not plantilla_facturas== None and not plantilla_devoluciones== None):
				msg = 'es valido'
				documentosData, polizas_de_devoluciones, msg = generar_polizas(fecha_ini, fecha_fin, ignorar_documentos_cont, crear_polizas_por, crear_polizas_de, plantilla_facturas, plantilla_devoluciones, descripcion)
			else:
				error =1
				msg = 'Seleciona una plantilla'

			if (crear_polizas_de == 'F' or crear_polizas_de=='FD') and documentosData == []:
				msg = 'Lo siento, no se encontraron facturas para este filtro'
			elif (crear_polizas_de == 'D' or crear_polizas_de=='FD') and polizas_de_devoluciones == []:
				msg = 'Lo siento, no se encontraron devoluciones para este filtro'
			
			if crear_polizas_de == 'FD' and documentosData == [] and polizas_de_devoluciones == []:
				msg = 'Lo siento, no se encontraron facturas ni devoluciones para este filtro'
			
	else:
		form = GenerarPolizasManageForm()
	
	c = {'documentos':documentosData, 'polizas_de_devoluciones':polizas_de_devoluciones,'msg':msg,'form':form,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='herramientas/plantilla_poliza.html'):
	message = ''

	if id:
		plantilla = get_object_or_404(PlantillaPolizas_V, pk=id)
	else:
		plantilla =PlantillaPolizas_V()

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
					Detalleplantilla.plantilla_poliza_v = plantilla
			
			plantilla_items_formset .save()
			return HttpResponseRedirect('/ventas/PreferenciasEmpresa/')
	else:
		plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_form= PlantillaPolizaManageForm(instance=plantilla)
	 	plantilla_items_formset  = plantilla_items(instance=plantilla)
	
	c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def plantilla_poliza_delete(request, id = None):
	plantilla = get_object_or_404(PlantillaPolizas_V, pk=id)
	plantilla.delete()

	return HttpResponseRedirect('/ventas/PreferenciasEmpresa/')

