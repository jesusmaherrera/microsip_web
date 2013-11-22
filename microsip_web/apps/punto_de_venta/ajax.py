 #encoding:utf-8
import json
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum, Max
import datetime, time
from django.db.models import Q

from decimal import *
from models import *
from microsip_web.libs.custom_db.main import next_id, get_existencias_articulo, first_or_none, get_sigfolio_ve
from django.db import transaction
from microsip_web.libs.custom_db.main import get_conecctionname

# @transaction.commit_manually
@dajaxice_register( method = 'GET' )
def generar_factura_global( request, **kwargs ):
    # Parametros
    connection_name = get_conecctionname(request.session)
    fecha_inicio = kwargs.get('fecha_inicio', None)
    fecha_fin = kwargs.get('fecha_fin', None)
    almacen_id = kwargs.get('almacen_id', None)
    fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y').date()
    fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y').date()
    almacen = first_or_none( Almacenes.objects.filter(pk=almacen_id) )
    cliente = Cliente.objects.get(pk=287)
    cliente_clave = first_or_none( ClavesClientes.objects.filter( cliente=cliente ) )
    cliente_direccion = DirCliente.objects.get(pk=292)

    if almacen:
        ventas_facturadas =  list( set( 
                DoctoPVLiga.objects.filter(docto_pv_fuente__almacen= almacen,docto_pv_fuente__fecha__gte = fecha_inicio, docto_pv_fuente__fecha__lte = fecha_fin).values_list( 'docto_pv_fuente__id', flat = True ) 
                ) ) 

        ventas_sin_facturar = Docto_PV.objects.exclude(id__in=ventas_facturadas).filter(almacen=almacen, tipo = 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)
        
        # for venta in ventas_sin_facturar:
        #     venta.clave_cliente_fac = cliente_clave.clave
        #     venta.cliente_fac = cliente
        #     venta.direccion_cliente = cliente_direccion
        #     venta.save(update_fields = [ 'clave_cliente_fac', 'cliente_fac', 'direccion_cliente', ])

        detalles = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas).\
            filter(documento_pv__almacen = almacen, documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin).\
            values('articulo').annotate(unidades=Sum('unidades'), precio_total_neto=Sum('precio_total_neto'), )

        detalles_factura = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas)\
            .filter(documento_pv__almacen = almacen, documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin)
        

        ventas_sinfacturar =  Docto_PV.objects.exclude( id__in = ventas_facturadas).filter(almacen =almacen, tipo= 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)

    else:
        ventas_facturadas =  list( set( 
                DoctoPVLiga.objects.filter(docto_pv_fuente__fecha__gte = fecha_inicio, docto_pv_fuente__fecha__lte = fecha_fin).values_list( 'docto_pv_fuente__id', flat = True ) 
                ) ) 

        ventas_sin_facturar = Docto_PV.objects.exclude(id__in=ventas_facturadas).filter(tipo = 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)
        
        detalles = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas).\
            filter(documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin).\
            values('articulo').annotate(unidades=Sum('unidades'), precio_total_neto=Sum('precio_total_neto'), )

        detalles_factura = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas)\
            .filter(documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin)
        

        ventas_sinfacturar =  Docto_PV.objects.exclude( id__in = ventas_facturadas).filter(tipo= 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)        
    # for detalle in detalles:
    #     detalle['unidades'] = str( detalle['unidades'] )
    #     detalle['precio_total_neto'] = str( detalle['precio_total_neto'] )
    message =''
    caja  = Caja.objects.get(pk=265)
    importe_neto = 80
    total_impuestos = 23
    importe_donativo,total_fpgc = 0, 0
    modalidad_facturacion = 'PREIMP'
    
    folio = get_sigfolio_ve(connection_name=connection_name, tipo_docto='F',serie='S')
    if ventas_sinfacturar.count() > 0:
        factura_global = Docto_PV.objects.create(
                id= next_id('ID_DOCTOS', connection_name),
                caja =  caja,
                tipo = 'F',
                folio = folio,
                fecha= datetime.now(),
                hora= datetime.now().strftime('%H:%M:%S'),
                clave_cliente= cliente_clave,
                cliente=cliente,
                clave_cliente_fac = cliente_clave,
                cliente_fac = cliente,
                direccion_cliente= cliente_direccion,
                moneda= Moneda.objects.get(pk=1),
                impuesto_incluido='N',
                tipo_cambio=1,
                tipo_descuento='I',
                porcentaje_descuento=0,
                importe_descuento=0,
                importe_neto = importe_neto ,
                total_impuestos= total_impuestos,
                importe_donativo= importe_donativo,
                total_fpgc= total_fpgc,
                sistema_origen='PV',
                persona='FACTURA GLOBAL DIARIA',
                descripcion='FACTURA GLOBAL(%s-%s)'%(fecha_inicio, fecha_fin),
                modalidad_facturacion = modalidad_facturacion,
                usuario_creador= request.user.username,
            )
        
        for detalle_factura in detalles_factura:
            Docto_pv_det.objects.create(
                    id = -1,
                    documento_pv = factura_global,
                    clave_articulo = detalle_factura.clave_articulo,
                    articulo = detalle_factura.articulo,
                    unidades = detalle_factura.unidades,
                    unidades_dev = detalle_factura.unidades_dev,
                    precio_unitario = detalle_factura.precio_unitario,
                    precio_unitario_impto = detalle_factura.precio_unitario_impto ,
                    fpgc_unitario = detalle_factura.fpgc_unitario ,
                    porcentaje_descuento = detalle_factura.porcentaje_descuento ,
                    precio_total_neto = detalle_factura.precio_total_neto ,
                    precio_modificado = detalle_factura.precio_modificado ,
                    vendedor = detalle_factura.vendedor ,
                    porcentaje_comis = detalle_factura.porcentaje_comis ,
                    rol = detalle_factura.rol ,
                    notas = detalle_factura.notas ,
                    es_tran_elect = detalle_factura.es_tran_elect ,
                    estatus_tran_elect = detalle_factura.estatus_tran_elect ,
                    posicion = -1,
                )

        for venta in ventas_sinfacturar:
            DoctoPVLiga.objects.create(
                    id = next_id('ID_LIGAS_DOCTOS', connection_name),
                    docto_pv_fuente = venta,
                    docto_pv_destino = factura_global,
                )
    else:
        message = 'No hay ventas por facturar'

    # detalles = str(detalles).replace("'",'"')
    
    return HttpResponse( json.dumps({"detalles": 'HOLA', 'message': message,}), mimetype = "application/javascript" )