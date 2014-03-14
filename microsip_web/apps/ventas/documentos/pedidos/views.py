#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
#Paginacion
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# user autentication
from django.contrib.auth.decorators import login_required
from models import *
from forms import *
from microsip_api.comun.sic_db import get_conecctionname

@login_required(login_url='/login/')
def pedido_manageview(request, id = None, template_name='ventas/documentos/pedidos/pedido.html'):
    if id:
        documento = get_object_or_404(VentasDocumento, pk=id)
    else:
        documento = VentasDocumento()
    
    #gruposgrupo_formset = formset_factory(form= GruposGrupo_ManageForm, can_delete=True,)

    if request.method == 'POST':
        doctove_items = DoctoVeDet_inlineformset(DoctoVeDet_ManageForm, extra=1, can_delete=True)
        formset = doctove_items(request.POST, request.FILES, instance=documento)
    else:
        doctove_items = DoctoVeDet_inlineformset(DoctoVeDet_ManageForm, extra=1, can_delete=True)
        formset = doctove_items(instance=documento)
        # gruposgrupomain_form  = GruposGrupoMain_ManageForm()
        # grupos_formset = gruposgrupo_formset()
        pedidoForm= DoctoVe_ManageForm(instance=documento)
        
    #'gruposgrupomain_form':gruposgrupomain_form,'grupos_formset':grupos_formset,
    c = {'pedidoForm': pedidoForm,'formset':formset,}

    return render_to_response(template_name, c, context_instance=RequestContext(request))

def pedidos_view(request, template_name='ventas/documentos/pedidos/pedidos.html'):
    pedidos = VentasDocumento.objects.filter(tipo='P')
    c = {'pedidos':pedidos, }
    return render_to_response(template_name, c, context_instance=RequestContext(request))   