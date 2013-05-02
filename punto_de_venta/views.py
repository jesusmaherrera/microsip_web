#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from forms import *
from models import *
from django.db.models import Q
from main.views import crear_polizas_contables
# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
#Paginacion

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
##########################################
## 										##
##        Generacion de polizas         ##
##										##
##########################################

def generar_polizas(fecha_ini=None, fecha_fin=None, ignorar_documentos_cont=True, crear_polizas_por='Documento', crear_polizas_de='', plantilla_ventas='', plantilla_devoluciones='', descripcion= ''):
	error 	= 0
	msg		= ''
	documentosData = []
	documentosGenerados = []
	documentosDataDevoluciones = []
	depto_co = get_object_or_404(DeptoCo,clave='GRAL')
	try:
		informacion_contable = InformacionContable_pv.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except ObjectDoesNotExist:
		error = 1
	
	#Si estadefinida la informacion contable no hay error!!!
	if error == 0:

		ventas 	= []
		devoluciones= []
		if ignorar_documentos_cont:
			if crear_polizas_de 	== 'V':
				ventas 			= Docto_PV.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D':
				devoluciones 		= Docto_PV.objects.filter(estado = 'N').filter(tipo ='D', contabilizado ='N',  fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		else:
			if crear_polizas_de 	== 'V':
				ventas 			= Docto_PV.objects.filter(Q(estado='N')|Q(estado='D'), tipo ='V', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
			elif crear_polizas_de 	== 'D':
				devoluciones 		= Docto_PV.objects.filter(estado = 'N').filter(tipo = 'D', fecha__gte=fecha_ini, fecha__lte=fecha_fin).order_by('fecha')[:99]
		
		if crear_polizas_de 	== 'V':
			msg, documentosData = crear_polizas_contables(
				origen_documentos	= 'punto_de_venta',
				documentos 			= ventas, 
				depto_co			= depto_co,
				informacion_contable= informacion_contable,
				plantilla 			= plantilla_ventas,
				crear_polizas_por	= crear_polizas_por,
				crear_polizas_de	= crear_polizas_de,
				msg = msg,
				descripcion = descripcion, 
				tipo_documento = 'V',
			)
			documentosGenerados = documentosData
		if crear_polizas_de 	== 'D':
			msg, documentosDataDevoluciones = crear_polizas_contables(
				origen_documentos	= 'punto_de_venta',
				documentos 			= devoluciones, 
				depto_co			= depto_co,
				informacion_contable= informacion_contable,
				plantilla 			= plantilla_devoluciones,
				crear_polizas_por	= crear_polizas_por,
				crear_polizas_de	= crear_polizas_de,
				msg = msg,
				descripcion = descripcion, 
				tipo_documento = 'D',
			)
			
	elif error == 1 and msg=='':
		msg = 'No se han derfinido las preferencias de la empresa para generar polizas [Por favor definelas primero en Configuracion > Preferencias de la empresa]'
	
	return documentosGenerados, documentosDataDevoluciones, msg

@login_required(login_url='/login/')
def generar_polizas_View(request, template_name='herramientas/generar_polizas_pv.html'):
	polizas_ventas	= []
	error 			= 0
	msg 	 		= ''

	if request.method == 'POST':
		form = GenerarPolizasManageForm(request.POST)
		if form.is_valid():

			fecha_ini 					= form.cleaned_data['fecha_ini']
			fecha_fin 					= form.cleaned_data['fecha_fin']
			ignorar_documentos_cont 	= form.cleaned_data['ignorar_documentos_cont']
			crear_polizas_por 			= form.cleaned_data['crear_polizas_por']
			crear_polizas_de 			= form.cleaned_data['crear_polizas_de']
			plantilla_ventas			= form.cleaned_data['plantilla_ventas']
			plantilla_devoluciones 		= form.cleaned_data['plantilla_devoluciones']
			plantilla_cobros_cc 		= form.cleaned_data['plantilla_cobros_cc']
			descripcion 				= form.cleaned_data['descripcion']

			if (crear_polizas_de == 'V' and not plantilla_ventas == None) or (crear_polizas_de == 'D' and not plantilla_devoluciones == None):
				msg = 'es valido'
				polizas_ventas, polizas_devoluciones, msg = generar_polizas(
					fecha_ini=fecha_ini, 
					fecha_fin=fecha_fin, 
					ignorar_documentos_cont=ignorar_documentos_cont, 
					crear_polizas_por=crear_polizas_por, 
					crear_polizas_de=crear_polizas_de, 
					plantilla_ventas=plantilla_ventas, 
					plantilla_devoluciones=plantilla_devoluciones, 
					descripcion= descripcion,
					)
			else:
				error =1
				msg = 'Seleciona una plantilla'

			if polizas_ventas== [] and not error == 1:
				msg = 'Lo siento, no se encontraron documentos para ralizar polizas con este filtro'
	else:
		form = GenerarPolizasManageForm()
	
	c = {'documentos':polizas_ventas,'msg':msg,'form':form,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
## 										##
##        Preferencias de empresa       ##
##										##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa_pv.html'):
	try:
		informacion_contable = InformacionContable_pv.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_pv()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	plantillas = PlantillaPolizas_pv.objects.all()
	c= {'form':form,'msg':msg,'plantillas':plantillas,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
## 										##
##              Plantillas              ##
##										##
##########################################

@login_required(login_url='/login/')
def plantilla_poliza_manageView(request, id = None, template_name='herramientas/plantilla_poliza_pv.html'):
	message = ''

	if id:
		plantilla = get_object_or_404(PlantillaPolizas_pv, pk=id)
	else:
		plantilla =PlantillaPolizas_pv()

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
					Detalleplantilla.plantilla_poliza_pv = plantilla
			
			plantilla_items_formset .save()
			return HttpResponseRedirect('/punto_de_venta/PreferenciasEmpresa/')
	else:
		plantilla_items = PlantillaPoliza_items_formset(ConceptoPlantillaPolizaManageForm, extra=1, can_delete=True)
		plantilla_form= PlantillaPolizaManageForm(instance=plantilla)
	 	plantilla_items_formset  = plantilla_items(instance=plantilla)
	
	c = {'plantilla_form': plantilla_form, 'formset': plantilla_items_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
## 										##
##            	Ventas                  ##
##										##
##########################################

@login_required(login_url='/login/')
def ventas_de_mostrador_view(request, template_name='documentos/ventas/ventas_de_mostrador.html'):
	ventas_list = Docto_PV.objects.filter(tipo='V')

	paginator = Paginator(ventas_list, 15) # Muestra 10 ventas por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		ventas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    ventas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    ventas = paginator.page(paginator.num_pages)

	c = {'ventas':ventas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def venta_mostrador_manageView(request, id = None, template_name='documentos/ventas/venta_de_mostrador.html'):
	
	message = ''
	hay_repetido = False
	if id:
		documento = get_object_or_404(Docto_PV, pk=id)
	else:
		documento = Docto_PV()
	
	documento_items = DocumentoPV_items_formset(DocumentoPVDet_ManageForm, extra=1, can_delete=True)
	documentoCobro_items = DocumentoPV_cobro_items_formset(Docto_pv_cobro_ManageForm, extra=1, can_delete=True)

	if request.method == 'POST':
		DocumentoForm = DocumentoPV_ManageForm(request.POST, request.FILES, instance=documento)
		documento_items_formset = documento_items(request.POST, request.FILES, instance=documento)
		documento_cobros_formset = documentoCobro_items(request.POST, request.FILES, instance=documento)
		
		if DocumentoForm.is_valid() and documento_items_formset.is_valid():
			documento = DocumentoForm.save(commit = False)

			documento.cajero = Cajero.objects.filter(usuario='PRUEBA')
			
			#CARGA NUEVO ID
			if not documento.id:
				documento.id = c_get_next_key('ID_DOCTOS')
			
			documento.save()

			#GUARDA ARTICULOS DE Documento
			for articulo_form in documento_items_formset:
				detalle_documento = articulo_form.save(commit = False)
				#PARA CREAR UNO NUEVO
				if not detalle_documento.id:
					detalle_documento.id = -1
					detalle_documento.docto_invfis = documento

				documento_items_formset.save()
			return HttpResponseRedirect('/punto_de_venta/ventas/')
	else:
		DocumentoForm= DocumentoPV_ManageForm(instance=documento)
		documento_cobros_formset = documentoCobro_items(instance=documento)
		documento_items_formset = documento_items(instance=documento)
	
	c = {'documentoForm': DocumentoForm, 'formset': documento_items_formset,'cobros_formset':documento_cobros_formset , 'message':message,}

	return render_to_response(template_name, c, context_instance=RequestContext(request))

##########################################
## 										##
##            	Devoluciones            ##
##										##
##########################################

@login_required(login_url='/login/')
def devoluciones_de_ventas_view(request, template_name='documentos/devoluciones/devoluciones_de_ventas.html'):
	documentos_list = Docto_PV.objects.filter(tipo='D')
	
	paginator = Paginator(documentos_list, 15) # Muestra 10 documentos por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		documentos = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    documentos = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    documentos = paginator.page(paginator.num_pages)
	
	c = {'documentos':documentos}
	return render_to_response(template_name, c, context_instance=RequestContext(request))