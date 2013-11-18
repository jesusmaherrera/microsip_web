#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from models import *
from forms import *
from django.db.models import Sum, Max
from microsip_web.libs.custom_db.main import get_conecctionname, next_id
# user autentication
from django.contrib.auth.decorators import login_required, permission_required

@login_required( login_url = '/login/' )
def generar_tarjetas( request, template_name = 'punto_de_venta/herramientas/generar_tarjetas.html' ):
    msg = ''
    connection_name = get_conecctionname(request.session)
    form = generartarjetas_form(request.POST or None)

    if form.is_valid():
        
        iniciar_en = form.cleaned_data[ 'iniciar_en' ]
        prefijo = form.cleaned_data[ 'prefijo' ]
        cantidad = form.cleaned_data[ 'cantidad' ]
        tipo_tarjeta = form.cleaned_data[ 'tipo_tarjeta' ]
        puntos = form.cleaned_data[ 'puntos' ]
        dinero_electronico = form.cleaned_data[ 'dinero_electronico' ]
        hereda_valorpuntos = form.cleaned_data[ 'hereda_valorpuntos' ]
        valor_puntos = form.cleaned_data[ 'valor_puntos' ]
        hereda_puntos_a = form.cleaned_data[ 'hereda_puntos_a' ]

        claves = []

        #Datos para cliente
        rolclaves = RolClavesClientes.objects.get( es_ppal = 'S' )
        moneda_local = Moneda.objects.get( es_moneda_local = 'S' )
        
        try:
            condicion_pago = CondicionPago.objects.get( es_predet = 'S' )
        except ObjectDoesNotExist:
            condicion_pago = CondicionPago.objects.all()[0]
        
        try:            
            tipo_cliente = TipoCliente.objects.get( nombre = 'TARJETA PROMOCION' )
        except ObjectDoesNotExist:
            tipo_cliente = TipoCliente.objects.create(id=-1, nombre = 'TARJETA PROMOCION', valor_puntos = 1)

        for numero in range( iniciar_en, iniciar_en + cantidad ):
            clave = '%s%s'% ( prefijo, ( "%09d" % numero ) )
            cliente = Cliente.objects.create(
                id = next_id( 'ID_CATALOGOS', connection_name ), 
                nombre = clave, 
                moneda = moneda_local, 
                condicion_de_pago = condicion_pago, 
                tipo_cliente = tipo_cliente,
                tipo_tarjeta = tipo_tarjeta,
                puntos = puntos,
                dinero_electronico = dinero_electronico,
                hereda_valorpuntos = hereda_valorpuntos,
                valor_puntos = valor_puntos,
                hereda_puntos_a = hereda_puntos_a,
                )

            ClavesClientes.objects.create( id = -1, clave = clave, cliente = cliente, rol =  rolclaves )
        msg = 'Clientes generados correctamente.'
        form = generartarjetas_form()

    c= { 'form' : form, 'msg' : msg, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )