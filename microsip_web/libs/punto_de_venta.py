 #encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db import connections
from django.db.models import Q
from decimal import *
import datetime, time

#Modelos de modulos 
from microsip_web.apps.punto_de_venta.models import *

#libs
from custom_db.main import next_id, first_or_none, runsql_rows

def new_factura_global( **kwargs ):
    ''' Genera una factura global '''
    
    #Parametros
    connection_name = kwargs.get('connection_name', None)
    username = kwargs.get('username', None)
    fecha_inicio = kwargs.get('fecha_inicio', None)
    fecha_fin = kwargs.get('fecha_fin', None)
    
    almacen = kwargs.get('almacen', None)
    cliente = kwargs.get('cliente', None)
    cliente_direccion = kwargs.get('cliente_direccion', None)
    cliente_clave = first_or_none( ClienteClave.objects.filter( cliente=cliente ) )
    
    factura_tipo = kwargs.get('factura_tipo', None)
    modalidad_facturacion = kwargs.get('modalidad_facturacion', None)

    detalles_list =[]
    ventas_list = []
    # Ventas facturadas
    ventas_facturadas = PuntoVentaDocumentoLiga.objects.filter(docto_pv_fuente__fecha__gte = fecha_inicio, docto_pv_fuente__fecha__lte = fecha_fin)
    if almacen:
        ventas_facturadas = ventas_facturadas.filter(docto_pv_fuente__almacen= almacen)
    ventas_facturadas_list =  list( set( ventas_facturadas.values_list( 'docto_pv_fuente__id', flat = True ) ) ) 

    # Ventas sin facturar
    ventas_sinfacturar =  PuntoVentaDocumento.objects.exclude( id__in = ventas_facturadas_list).exclude(estado='C').filter(tipo= 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)
    
    detalles_factura = PuntoVentaDocumentoDetalle.objects.exclude(documento_pv__estado='C').exclude(documento_pv__id__in = ventas_facturadas_list)\
       .filter(documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin)
    if almacen:
        ventas_sinfacturar = ventas_sinfacturar.filter(almacen = almacen)
        detalles_factura = detalles_factura.filter(documento_pv__almacen = almacen)
    
    ventas_sinfacturar_list =  list( set( ventas_sinfacturar.order_by('folio',).values_list( 'id', flat = True ) ) ) 

    # Totales factura global
    totales = ventas_sinfacturar.aggregate(
            importe_neto=Sum('importe_neto',),  
            total_impuestos=Sum('total_impuestos',),
            importe_donativo=Sum('importe_donativo',),
            total_fpgc=Sum('total_fpgc',),
            importe_descuento=Sum('importe_descuento',),
        )

    importe_neto = totales['importe_neto']
    total_impuestos = totales['total_impuestos']
    importe_donativo = totales['importe_donativo']
    total_fpgc = totales['total_fpgc']
    importe_descuento = totales['importe_descuento']

    message =''
    impuestos = []

    # si hay ventas por facturar
    if ventas_sinfacturar.count() > 0:
        for venta in ventas_sinfacturar:
            # detalles_venta = list( set( PuntoVentaDocumentoDetalle.objects.filter(documento_pv=venta).values_list( 'id', flat = True ) ) ) 
            ventas_list.append({
                    'id':venta.id,
                    'folio': venta.folio,
                    'fecha':str(venta.fecha),
                    'importe_neto':str(venta.importe_neto),
                    # 'detalles': detalles_venta,
                })
        
        impuestos_doc =  PuntoVentaDocumentoImpuesto.objects.filter(documento_pv__in=ventas_sinfacturar_list).filter(venta_neta__gt=0).values('impuesto','porcentaje_impuestos').annotate(
                venta_neta = Sum('venta_neta'),
                otros_impuestos = Sum('otros_impuestos'),
                importe_impuesto = Sum('importe_impuesto'),
            )
        
        if factura_tipo == 'P':
            
            articulo_ventaspg_id = Registry.objects.get( nombre = 'ARTICULO_VENTAS_FG_PV_ID' ).valor
            articulo = Articulo.objects.get(pk=articulo_ventaspg_id)
            articulo_clave = first_or_none(ArticuloClave.objects.filter(articulo=articulo))
            if articulo_clave:
                articulo_clave = articulo_clave.clave
            articulo_nombre = articulo.nombre
            articulo_id = articulo.id
            detalles_list.append({
                    'articulo_nombre':articulo_nombre, 
                    'articulo_id': articulo_id, 
                    'articulo_clave': articulo_clave,
                    'precio': str(importe_neto),
                    'porcentaje_descuento': 0,
                    'unidades':1,
                    'precio_total_neto': str(importe_neto),
                })
        
        
        for impuesto in impuestos_doc:
            impuestos.append({
                    'venta_neta': str(impuesto['venta_neta']),
                    'otros_impuestos': str(impuesto['otros_impuestos']),
                    'importe_impuesto': str(impuesto['importe_impuesto']),
                    'porcentaje_impuestos': str(impuesto['porcentaje_impuestos']),
                    'impuestos_ids': str(impuesto['impuesto'])
                })

        if factura_tipo == 'C':
            detalles_factura_concentrada = detalles_factura.values('articulo').annotate(
                    sum_unidades = Sum('unidades'),
                    sum_precio_total_neto = Sum('precio_total_neto'),
                )
                            
            for detalle in detalles_factura_concentrada:
                articulo = Articulo.objects.get(pk=detalle['articulo'])
                detalles_relacion = list( set( detalles_factura.filter(articulo=articulo).values_list( 'id', flat = True ) ) )

                articulo_clave = first_or_none(ArticuloClave.objects.filter(articulo=articulo))
                if articulo_clave:
                    articulo_clave = articulo_clave.clave

                unidades = detalle['sum_unidades']
                precio_total_neto = detalle['sum_precio_total_neto']
                
                precio = precio_total_neto / unidades

                detalles_list.append({
                        'articulo_nombre':articulo.nombre, 
                        'articulo_id': articulo.id, 
                        'articulo_clave': articulo_clave,
                        'precio': str(precio),
                        'porcentaje_descuento': 0,
                        'unidades':str(unidades),
                        'precio_total_neto': str(precio_total_neto),
                        'detalles_relacion': detalles_relacion,
                    })
        elif factura_tipo == 'D':
            for detalle_factura in detalles_factura:
                detalles_list.append({
                        'articulo_nombre':detalle_factura.articulo.nombre, 
                        'articulo_id': detalle_factura.articulo.id, 
                        'articulo_clave': detalle_factura.clave_articulo,
                        'precio': str(detalle_factura.precio_unitario), 
                        'porcentaje_descuento':str(detalle_factura.porcentaje_descuento),
                        'unidades':str(detalle_factura.unidades),
                        'precio_total_neto': str(detalle_factura.precio_total_neto),
                    })
    else:
        message = 'No hay ventas por facturar'

    totales_factura = {
        'importe_neto': str(importe_neto),
        'total_impuestos': str(total_impuestos),
        'importe_donativo': str(importe_donativo),
        'total_fpgc': str(total_fpgc),
        'importe_descuento': str(importe_descuento),
    }

    data = {
        'totales':totales_factura,
        'detalles': detalles_list,
        'ventas_facturadas':ventas_list,
        'message': message,
        'fecha_inicio':str(fecha_inicio),
        'fecha_fin':str(fecha_fin),
        'impuestos': impuestos,
    }

    return data