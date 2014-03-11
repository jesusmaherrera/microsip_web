#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from models import *
from microsip_web.apps.inventarios.models import *
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
from microsip_web.libs.custom_db.main import get_conecctionname

@login_required(login_url='/login/')
def polizas_View(request, template_name='contabilidad/polizas/polizas.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    polizas_list = ContabilidadDocumento.objects.filter(estatus='N').order_by('-fecha') 

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
def polizas_pendientesView(request, template_name='contabilidad/polizas/polizas_pendientes.html'):
    connection_name = get_conecctionname(request.session)
    if connection_name == '':
        return HttpResponseRedirect('/select_db/')

    polizas_list = ContabilidadDocumento.objects.filter(estatus='P').order_by('-fecha') 

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
def preferenciasEmpresa_View(request, template_name='contabilidad/herramientas/preferencias_empresa.html'):
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

# @login_required(login_url='/login/')
# def generar_diotView(request, template_name='herramientas/generar_diot.html'):

    
#   error =0
#   try:
#       informacion_contable = InformacionContable_C.objects.all()[:1]
#       informacion_contable = informacion_contable[0]
#   except:
#       msg = 'No se ha definido la informacion contable aun.'
#       error = 1
#       formset =[]

#   if error == 0:
#       msg=''
#       cuentas_provedores = ContabilidadCuentaContable.objects.filter(cuenta__contains=informacion_contable.cuenta_proveedores.cuenta)
#       cuentas_diot = Cuenta_DIOT.objects.all()
#       #objects.sd
#       if request.method == 'POST':
            
#           formset = Cuenta_DIOTFormset(request.POST)
#           generarDIOT_form = GenerarDIOTManageForm(request.POST, prefix="generarDIOT")
#           if formset.is_valid() and generarDIOT_form.is_valid():
                
#               formset.save()
#               fecha_ini = generarDIOT_form.cleaned_data['fecha_ini']
#               fecha_fin = generarDIOT_form.cleaned_data['fecha_fin']
                
#               file_DIOT=open('C:\Users\Admin\Documents\DIOT.txt','w')
#               for form in formset:
#                   form = form.save(commit=False)
#                   #| Q(fecha_lte=fecha_fin),
#                   suma_a = ContabilidadDocumentoDetalle.objects.filter(cuenta=form.cuenta, tipo_asiento='A', fecha__gte=fecha_ini).aggregate(suma_a = Sum('importe'))['suma_a']
#                   if suma_a == None:
#                       suma_a = 0
#                   suma_c = ContabilidadDocumentoDetalle.objects.filter(cuenta=form.cuenta,fecha__gte=fecha_ini, tipo_asiento='C').aggregate(suma_c = Sum('importe'))['suma_c']
#                   if suma_c == None:
#                       suma_c = 0

#                   file_DIOT.write('rfc: %s, importe cuenta(%s):%s(A),%s(B)\n'% (form.rfc,form.cuenta.cuenta, suma_a, suma_c))

#               file_DIOT.close()
#               msg = 'Datos Guardados'
                
#       else:
#           generarDIOT_form = GenerarDIOTManageForm(prefix="generarDIOT")
#           if cuentas_diot.count() == 0:
#               for cuenta_proveedor in cuentas_provedores:
#                   Cuenta_DIOT.objects.create(cuenta=cuenta_proveedor,tipo_proveedor='04', tipo_operacion='03',rfc='')
#                   cuentas_diot = Cuenta_DIOT.objects.all()

#           formset = Cuenta_DIOTFormset(queryset=cuentas_diot)

#   c= {'formset':formset,'msg':msg,'generarDIOT_form':generarDIOT_form,}
#   return render_to_response(template_name, c, context_instance= RequestContext(request))
