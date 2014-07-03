 #encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum, Max, Avg
from django.db import transaction
from django.db.models import Q
from django.db import connections

from dajaxice.decorators import dajaxice_register

import datetime, time, json
from decimal import *
from models import *

from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none, get_conecctionname
from microsip_web.libs.punto_de_venta import new_factura_global

# @dajaxice_register( method = 'GET' )
# def aplicar_doctopv( request, **kwargs ):
#     docto_id = kwargs.get( 'docto_id', None )
#     documento = PuntoVentaDocumento.objects.get(pk=docto_id)
#     documento.aplicado ='S'
#     documento.save()
#     return json.dumps( { 'msg' : 'ya'} )

# @transaction.commit_manually
@dajaxice_register( method = 'GET' )
def generar_factura_global( request, **kwargs ):

    # Parametros
    connection_name = get_conecctionname(request.session)
    fecha_inicio = datetime.datetime.strptime( kwargs.get( 'fecha_inicio', None ), '%d/%m/%Y' ).date()
    # fecha_fin = datetime.strptime( kwargs.get( 'fecha_inicio', None ), '%d/%m/%Y' ).date()
    fecha_fin = datetime.datetime.strptime( kwargs.get( 'fecha_fin', None ), '%d/%m/%Y' ).date()
    almacen = first_or_none( Almacen.objects.filter( pk = kwargs.get('almacen_id', None) ) )
    cliente = Cliente.objects.get( pk = int( kwargs.get('cliente_id', None) ) )
    cliente_direccion =  first_or_none( ClienteDireccion.objects.filter(cliente=cliente) )
    factura_tipo = kwargs.get('factura_tipo', None)
    modalidad_facturacion = kwargs.get('modalidad_facturacion', None)

    #SI NO EXITE ARICULO DE PUBLICO EN GENERAL
    articulo_ventaspg_id = Registry.objects.get( nombre = 'ARTICULO_VENTAS_FG_PV_ID' )
    articulo_ventaspg_id.save(update_fields=['valor',])
    if not Articulo.objects.filter(pk=articulo_ventaspg_id.valor).exists() and factura_tipo == 'P':
        c = {'message':'por favor primero espesifica un articulo general',}
        return HttpResponse( json.dumps(c), mimetype = "application/javascript" )
    
    if cliente_direccion.rfc_curp != "XAXX010101000":
        c = {'message':'Una factura global solo puede realizar a clientes con \nRFC: XAXX010101000',}
        return HttpResponse( json.dumps(c), mimetype = "application/javascript" )

    data = new_factura_global(
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            almacen = almacen,
            cliente = cliente,
            cliente_direccion = cliente_direccion,
            factura_tipo = factura_tipo,
            modalidad_facturacion = modalidad_facturacion,
            connection_name = connection_name,
            username = request.user.username
        )

    c = {
        'detalles': data['detalles'], 
        'totales': data['totales'],
        'ventas_facturadas':data['ventas_facturadas'],
        'message': data['message'],
        'fecha_inicio': data['fecha_inicio'],
        'fecha_fin':data['fecha_fin'],
        'impuestos': data['impuestos'],
        }

    return HttpResponse( json.dumps(c), mimetype = "application/javascript" )