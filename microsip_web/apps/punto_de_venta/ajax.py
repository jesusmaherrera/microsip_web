 #encoding:utf-8
import json
from dajaxice.decorators import dajaxice_register
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum, Max, Avg
import datetime, time
from django.db.models import Q
from django.db import connections
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
    cliente_id = kwargs.get('cliente_id', None)
    factura_tipo = kwargs.get('factura_tipo', None)
    modalidad_facturacion = kwargs.get('modalidad_facturacion', None)

    fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y').date()
    fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y').date()
    almacen = first_or_none( Almacenes.objects.filter(pk=almacen_id) )
    cliente = Cliente.objects.get(pk=int(cliente_id))
    cliente_clave = first_or_none( ClavesClientes.objects.filter( cliente=cliente ) )
    cliente_direccion =  first_or_none( DirCliente.objects.filter(cliente=cliente) )
    
    ventas_facturadas = DoctoPVLiga.objects.filter(docto_pv_fuente__fecha__gte = fecha_inicio, docto_pv_fuente__fecha__lte = fecha_fin)
    
    if almacen:
        ventas_facturadas = ventas_facturadas.filter(docto_pv_fuente__almacen= almacen)

    ventas_facturadas_list =  list( set( ventas_facturadas.values_list( 'docto_pv_fuente__id', flat = True ) ) ) 
    ventas_sinfacturar =  Docto_PV.objects.exclude( id__in = ventas_facturadas_list).filter(tipo= 'V', fecha__gte = fecha_inicio, fecha__lte = fecha_fin)
    detalles_factura = Docto_pv_det.objects.exclude(documento_pv__id__in = ventas_facturadas_list)\
       .filter(documento_pv__tipo = 'V',documento_pv__fecha__gte= fecha_inicio, documento_pv__fecha__lte=fecha_fin)

    if almacen:
        ventas_sinfacturar = ventas_sinfacturar.filter(almacen = almacen)
        detalles_factura = detalles_factura.filter(documento_pv__almacen = almacen)
    
    #Calcula totales
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
    folio = get_sigfolio_ve(connection_name=connection_name, tipo_docto='F',serie='S')

    #Se crea factura y ligas
    if ventas_sinfacturar.count() > 0:
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
                usuario_creador= request.user.username,
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
            query =  '''SELECT DOCTOS_PV_DET.articulo_id, SUM(DOCTOS_PV_DET.unidades), SUM(DOCTOS_PV_DET.precio_unitario_impto*DOCTOS_PV_DET.unidades) as total_unidades\
                FROM DOCTOS_PV_DET INNER JOIN DOCTOS_PV ON (DOCTOS_PV_DET.DOCTO_PV_ID = DOCTOS_PV.DOCTO_PV_ID)\
                WHERE\
                    DOCTOS_PV.tipo_docto ='V' and\
                    DOCTOS_PV.fecha >= '%s' AND DOCTOS_PV.fecha <= '%s' AND\
                    not DOCTOS_PV.docto_pv_id in %s\
                group by DOCTOS_PV_DET.articulo_id\
                '''%(fecha_inicio, fecha_fin, tuple(ventas_facturadas_list))
            c.execute(query)
            detalles_factura_concentrada = c.fetchall()
            c.close()
            
            for detalle in detalles_factura_concentrada:
                articulo = Articulos.objects.get(pk=detalle[0])
                articulo_clave = first_or_none(ClavesArticulos.objects.filter(articulo=articulo))
                unidades = detalle[1]
                precio_promedio = detalle[2]/ unidades
                precio_total_neto =  precio_promedio * unidades
                Docto_pv_det.objects.create(
                        id = -1,
                        documento_pv = factura_global,
                        clave_articulo = articulo_clave,
                        articulo = articulo,
                        unidades = detalle[1],
                        unidades_dev = 0,
                        precio_unitario = precio_promedio,
                        precio_unitario_impto = 0 ,
                        fpgc_unitario = 0 ,
                        porcentaje_descuento = 0 ,
                        precio_total_neto =precio_total_neto,
                        precio_modificado = 'P' ,
                        porcentaje_comis = 0 ,
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

    # detalles = str(detalles).replace("'",'"')
    
    return HttpResponse( json.dumps({"detalles": 'HOLA', 'message': message,}), mimetype = "application/javascript" )