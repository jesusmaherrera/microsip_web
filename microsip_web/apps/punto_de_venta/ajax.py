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

from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none, get_sigfolio_ve, get_conecctionname
from microsip_web.libs.punto_de_venta import new_factura_global

# @transaction.commit_manually
@dajaxice_register( method = 'GET' )
def generar_factura_global( request, **kwargs ):
    # Parametros
    connection_name = get_conecctionname(request.session)
    fecha_inicio = datetime.strptime( kwargs.get( 'fecha_inicio', None ), '%d/%m/%Y' ).date()
    fecha_fin = datetime.strptime( kwargs.get( 'fecha_fin', None ), '%d/%m/%Y' ).date()
    almacen = first_or_none( Almacenes.objects.filter( pk = kwargs.get('almacen_id', None) ) )
    cliente = Cliente.objects.get( pk = int( kwargs.get('cliente_id', None) ) )
    
    factura_tipo = kwargs.get('factura_tipo', None)
    modalidad_facturacion = kwargs.get('modalidad_facturacion', None)

    message = new_factura_global(
            fecha_inicio=fecha_inicio,
            fecha_fin= fecha_fin,
            almacen= almacen,
            cliente= cliente,
            factura_tipo= factura_tipo,
            modalidad_facturacion= modalidad_facturacion,
            connection_name= connection_name,
            username = request.user.username
        )

    return HttpResponse( json.dumps({"detalles": 'HOLA', 'message': message,}), mimetype = "application/javascript" )