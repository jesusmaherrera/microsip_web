#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from models import *
from forms import *
#from contabilidad.forms import *
import datetime, time
from django.db.models import Q
#Paginacion
from django.forms.formsets import formset_factory

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max

@login_required(login_url='/login/')
def polizas_View(request, template_name='polizas/polizas.html'):
	polizas_list = DoctoCo.objects.filter(estatus='N').order_by('-fecha') 

	paginator = Paginator(polizas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		polizas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    polizas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    polizas = paginator.page(paginator.num_pages)

	c = {'polizas':polizas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def polizas_pendientesView(request, template_name='polizas/polizas_pendientes.html'):
	#polizas_list = DoctoCo.objects.using('db_chuy').filter(estatus='P').order_by('-fecha') 
	polizas_list = DoctoCo.objects.filter(estatus='P').order_by('-fecha') 

	paginator = Paginator(polizas_list, 15) # Muestra 5 inventarios por pagina
	page = request.GET.get('page')

	#####PARA PAGINACION##############
	try:
		polizas = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    polizas = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    polizas = paginator.page(paginator.num_pages)

	c = {'polizas':polizas}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='herramientas/preferencias_empresa_C.html'):
	try:
		informacion_contable = InformacionContable_C.objects.all()[:1]
		informacion_contable = informacion_contable[0]
	except:
		informacion_contable = InformacionContable_C()

	msg = ''
	if request.method == 'POST':
		form = InformacionContableManageForm(request.POST, instance=informacion_contable)
		if form.is_valid():
			form.save()
			msg = 'Datos Guardados Exitosamente'
	else:
		form = InformacionContableManageForm(instance=informacion_contable)

	c= {'form':form,'msg':msg,}
	return render_to_response(template_name, c, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def generar_diotView(request, template_name='herramientas/generar_diot.html'):
	if request.method == 'POST':
		formsetx = Cuenta_DIOTFormset(request.POST)
		
		if formsetx.is_valid():
			formsetx.save()

			return HttpResponseRedirect('/contabilidad/polizas/')
	else:
		formsetx = Cuenta_DIOTFormset(queryset=Cuenta_DIOT.objects.all())
		#formset = Cuenta_DIOTFormset()

	c= {'formset':formsetx,}
	return render_to_response(template_name, c, context_instance= RequestContext(request))
