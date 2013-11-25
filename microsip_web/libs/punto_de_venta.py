 #encoding:utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db import connections

from decimal import *
import datetime, time

#Modelos de modulos 
from microsip_web.apps.punto_de_venta.models import *

#libs
from custom_db.main import next_id, first_or_none, get_sigfolio_ve

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
     
    # si hay ventas por facturar
    if ventas_sinfacturar.count() > 0:
        folio = get_sigfolio_ve(connection_name=connection_name, tipo_docto='F',serie='S')

        factura_global = Docto_PV.objects.create(
                id= next_id('ID_DOCTOS', connection_name),
                caja = first_or_none( Caja.objects.all() ) ,
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
                importe_descuento = importe_descuento,
                importe_neto = importe_neto ,
                total_impuestos= total_impuestos,
                importe_donativo= importe_donativo,
                total_fpgc= total_fpgc,
                sistema_origen='PV',
                persona='FACTURA GLOBAL DIARIA',
                descripcion='FACTURA GLOBAL(%s-%s)'%(fecha_inicio, fecha_fin),
                modalidad_facturacion = modalidad_facturacion,
                usuario_creador= username,
            )

        for venta in ventas_sinfacturar:
            DoctoPVLiga.objects.create(
                    id = next_id('ID_LIGAS_DOCTOS', connection_name),
                    docto_pv_fuente = venta,
                    docto_pv_destino = factura_global,
                )
        #Se crean los detalles segun el tipo de fatura
        if factura_tipo == 'C':
            c = connections[connection_name].cursor()
            if almacen:
                query =  '''SELECT DOCTOS_PV_DET.articulo_id, SUM(DOCTOS_PV_DET.unidades), SUM(DOCTOS_PV_DET.precio_unitario*DOCTOS_PV_DET.unidades) as total_unidades, SUM(DOCTOS_PV_DET.precio_unitario_impto)\
                    SUM(DOCTOS_PV_DET.PCTJE_DSCTO), SUM(DOCTOS_PV_DET.PCTJE_COMIS), SUM(DOCTOS_PV_DET.fpgc_unitario), SUM(DOCTOS_PV_DET.unidades_dev)  \
                    FROM DOCTOS_PV_DET INNER JOIN DOCTOS_PV ON (DOCTOS_PV_DET.DOCTO_PV_ID = DOCTOS_PV.DOCTO_PV_ID)\
                    WHERE\
                        DOCTOS_PV.almacen_id = %s and\
                        DOCTOS_PV.tipo_docto ='V' and\
                        DOCTOS_PV.fecha >= '%s' AND DOCTOS_PV.fecha <= '%s' AND\
                        not DOCTOS_PV.docto_pv_id in %s\
                    group by DOCTOS_PV_DET.articulo_id\
                    '''%(almacen.ALMACEN_ID, fecha_inicio, fecha_fin, str(tuple(ventas_facturadas_list)))
            else:
                query =  '''SELECT DOCTOS_PV_DET.articulo_id, SUM(DOCTOS_PV_DET.unidades), SUM(DOCTOS_PV_DET.precio_unitario*DOCTOS_PV_DET.unidades) as total_unidades, SUM(DOCTOS_PV_DET.precio_unitario_impto),\
                    SUM(DOCTOS_PV_DET.PCTJE_DSCTO), SUM(DOCTOS_PV_DET.PCTJE_COMIS), SUM(DOCTOS_PV_DET.fpgc_unitario), SUM(DOCTOS_PV_DET.unidades_dev)  \
                    FROM DOCTOS_PV_DET INNER JOIN DOCTOS_PV ON (DOCTOS_PV_DET.DOCTO_PV_ID = DOCTOS_PV.DOCTO_PV_ID)\
                    WHERE\
                        DOCTOS_PV.tipo_docto ='V' and\
                        DOCTOS_PV.fecha >= '%s' AND DOCTOS_PV.fecha <= '%s' AND\
                        not DOCTOS_PV.docto_pv_id in %s\
                    group by DOCTOS_PV_DET.articulo_id\
                    '''%(fecha_inicio, fecha_fin, str(tuple(ventas_facturadas_list)))

            c.execute(query)
            detalles_factura_concentrada = c.fetchall()
            c.close()
            
            for detalle in detalles_factura_concentrada:
                articulo = Articulos.objects.get(pk=detalle[0])
                articulo_clave = first_or_none(ClavesArticulos.objects.filter(articulo=articulo))
                unidades = detalle[1]
                precio_promedio = detalle[2]/ unidades
                total_precio_unitario_impt = detalle[3]
                porcentaje_descuento = detalle[4]
                precio_total_neto =  precio_promedio * unidades
                porcentaje_comis = detalle[5]
                fpgc_unitario = detalle[6]
                unidades_dev = detalle[7]

                Docto_pv_det.objects.create(
                        id = -1,
                        documento_pv = factura_global,
                        clave_articulo = articulo_clave,
                        articulo = articulo,
                        unidades = detalle[1],
                        unidades_dev = unidades_dev,
                        precio_unitario = precio_promedio,
                        precio_unitario_impto = total_precio_unitario_impt,
                        fpgc_unitario = fpgc_unitario ,
                        porcentaje_descuento = porcentaje_descuento ,
                        precio_total_neto =precio_total_neto,
                        precio_modificado = 'P' ,
                        porcentaje_comis = porcentaje_comis ,
                        rol = 'N' ,
                        posicion = -1,
                    )          
        elif factura_tipo == 'D':
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
    else:
        message = 'No hay ventas por facturar'

    return message