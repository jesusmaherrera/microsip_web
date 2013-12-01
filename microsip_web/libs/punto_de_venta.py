 #encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db import connections

from decimal import *
import datetime, time

#Modelos de modulos 
from microsip_web.apps.punto_de_venta.models import *

#libs
from custom_db.main import next_id, first_or_none, get_sigfolio_ve, runsql_rows

def new_factura_global( **kwargs ):
    ''' Genera una factura global '''
    
    #Parametros
    connection_name = kwargs.get('connection_name', None)
    username = kwargs.get('username', None)
    fecha_inicio = kwargs.get('fecha_inicio', None)
    fecha_fin = kwargs.get('fecha_fin', None)
    
    almacen = kwargs.get('almacen', None)
    cliente = kwargs.get('cliente', None)
    cliente_clave = first_or_none( ClavesClientes.objects.filter( cliente=cliente ) )
    cliente_direccion =  first_or_none( DirCliente.objects.filter(cliente=cliente) )

    factura_tipo = kwargs.get('factura_tipo', None)
    modalidad_facturacion = kwargs.get('modalidad_facturacion', None)

    detalles_list =[]
    ventas_list = []
    # Ventas facturadas
    ventas_facturadas = DoctoPVLiga.objects.filter(docto_pv_fuente__fecha__gte = fecha_inicio, docto_pv_fuente__fecha__lte = fecha_fin)
    if almacen:
        ventas_facturadas = ventas_facturadas.filter(docto_pv_fuente__almacen= almacen)
    ventas_facturadas_list =  list( set( ventas_facturadas.values_list( 'docto_pv_fuente__id', flat = True ) ) ) 

    # Ventas sin facturar
    ventas_sinfacturar =  Docto_PV.objects.exclude( id__in = ventas_facturadas_list).filter(tipo= 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)
    detalles_factura = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas_list)\
       .filter(documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin)
    if almacen:
        ventas_sinfacturar = ventas_sinfacturar.filter(almacen = almacen)
        detalles_factura = detalles_factura.filter(documento_pv__almacen = almacen)
    
    ventas_sinfacturar_list =  list( set( ventas_sinfacturar.values_list( 'id', flat = True ) ) ) 

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
    impuestos_doc= ''
    
    # si hay ventas por facturar
    if ventas_sinfacturar.count() > 0:
        for venta in ventas_sinfacturar:
            ventas_list.append({
                    'id':venta.id,
                    'folio': venta.folio,
                    'fecha':str(venta.fecha),
                    'importe_neto':str(venta.importe_neto),
                })
        
        impuestos_doc =  Impuestos_docto_pv.objects.filter(documento_pv__in=ventas_sinfacturar_list).aggregate(
                venta_neta = Sum('venta_neta'),
                otros_impuestos = Sum('otros_impuestos'),
                importe_impuesto = Sum('importe_impuesto'),
            )
        
        if factura_tipo == 'P':
            precio_total_neto = detalles_factura.aggregate(Sum('precio_total_neto'))['precio_total_neto__sum']
            articulo_precio_unitario = precio_total_neto - impuestos_doc['importe_impuesto']
            
            articulo_ventaspg_id = Registry.objects.get( nombre = 'ARTICULO_VENTAS_FG_PV_ID' ).valor
            articulo = Articulos.objects.get(pk=articulo_ventaspg_id)
            articulo_clave = first_or_none(ClavesArticulos.objects.filter(articulo=articulo))
            if articulo_clave:
                articulo_clave = articulo_clave.clave
            articulo_nombre = articulo.nombre
            articulo_id = articulo.id

            detalles_list.append({
                    'articulo_nombre':articulo_nombre, 
                    'articulo_id': articulo_id, 
                    'articulo_clave': articulo_clave,
                    'precio': str(articulo_precio_unitario),
                    'porcentaje_descuento': 0,
                    'unidades':1,
                    'precio_total_neto': str(articulo_precio_unitario),
                })
        
        impuestos_doc['venta_neta'] = str(impuestos_doc['venta_neta'])
        impuestos_doc['otros_impuestos'] = str(impuestos_doc['otros_impuestos'])
        impuestos_doc['importe_impuesto'] = str(impuestos_doc['importe_impuesto'])

        if factura_tipo == 'C':
            exclude =''
            if ventas_facturadas_list != []:
                exclude = " AND not DOCTOS_PV.docto_pv_id in %s"%str(tuple(ventas_facturadas_list))
            sql_almacen_filter= ""
            if almacen:
                sql_almacen_filter = " DOCTOS_PV.almacen_id = %s AND"%almacen.ALMACEN_ID

            sql_concentrado = "SELECT \
                DOCTOS_PV_DET.articulo_id, \
                SUM(DOCTOS_PV_DET.unidades) as sum_unidades, \
                SUM(DOCTOS_PV_DET.precio_unitario*DOCTOS_PV_DET.unidades) as importe_neto, \
                SUM(DOCTOS_PV_DET.precio_unitario_impto) as sum_precioimpto,\
                SUM(DOCTOS_PV_DET.PCTJE_DSCTO) as sum_PCTJE_DSCTO, \
                SUM(DOCTOS_PV_DET.PCTJE_COMIS) as sum_PCTJE_COMIS, \
                SUM(DOCTOS_PV_DET.fpgc_unitario) as sum_fpgc_unitario, \
                SUM(DOCTOS_PV_DET.unidades_dev) as sum_unidades_dev\
            FROM DOCTOS_PV_DET INNER JOIN DOCTOS_PV ON (DOCTOS_PV_DET.DOCTO_PV_ID = DOCTOS_PV.DOCTO_PV_ID)\
            WHERE"+ sql_almacen_filter + "\
                DOCTOS_PV.tipo_docto ='V' and\
                DOCTOS_PV.fecha >= %s AND DOCTOS_PV.fecha <= %s"+ exclude +"group by DOCTOS_PV_DET.articulo_id"

            detalles_factura_concentrada = runsql_rows( 
                    sql = sql_concentrado,
                    connection_name = connection_name,
                    params = [fecha_inicio, fecha_fin]
                )
            
            for detalle in detalles_factura_concentrada:
                articulo = Articulos.objects.get(pk=detalle[0])
                articulo_clave = first_or_none(ClavesArticulos.objects.filter(articulo=articulo))
                if articulo_clave:
                    articulo_clave = articulo_clave.clave
                articulo_nombre = articulo.nombre
                articulo_id = articulo.id

                unidades = detalle[1]
                precio_promedio = detalle[2]/ unidades
                total_precio_unitario_impt = detalle[3]
                precio_total_neto =  precio_promedio * unidades
                porcentaje_comis = detalle[5]
                fpgc_unitario = detalle[6]
                unidades_dev = detalle[7]

                detalles_list.append({
                        'articulo_nombre':articulo_nombre, 
                        'articulo_id': articulo_id, 
                        'articulo_clave': articulo_clave,
                        'precio': str(precio_promedio),
                        'porcentaje_descuento': 0,
                        'unidades':str(unidades),
                        'precio_total_neto': str(precio_total_neto),
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
        'impuestos': impuestos_doc,
    }
    return data