#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.db.models import Q
from datetime import timedelta
from decimal import *
from django.core import serializers
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# user autentication
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max

import datetime, time

from models import *
from forms import *
from microsip_web.apps.inventarios.views import c_get_next_key
from microsip_web.libs import contabilidad
from microsip_api.comun.sic_db import get_conecctionname


##########################################
##                                      ##
##        Preferencias de empresa       ##
##                                      ##
##########################################

@login_required(login_url='/login/')
def preferenciasEmpresa_View(request, template_name='ventas/herramientas/preferencias_empresa.html'):
    try:
        informacion_contable = InformacionContable_V.objects.all()[:1]
        informacion_contable = informacion_contable[0]
    except:
        informacion_contable = InformacionContable_V()

    cuenta_cliente_formset = modelformset_factory(clientes_config_cuenta, form= clientes_config_cuentaManageForm, can_delete=True,)
    
    msg = ''
    if request.method == 'POST':
        formset = cuenta_cliente_formset(request.POST, request.FILES)

        form = InformacionContableManageForm(request.POST, instance=informacion_contable)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            formset = cuenta_cliente_formset()
            msg = 'Datos Guardados Exitosamente'
    else:
        form = InformacionContableManageForm(instance=informacion_contable)
        formset = cuenta_cliente_formset()
        
    plantillas = PlantillaPolizas_V.objects.all()
    c= {'form':form,'msg':msg,'plantillas':plantillas,'formset':formset,}
    return render_to_response(template_name, c, context_instance=RequestContext(request))



