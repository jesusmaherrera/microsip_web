#encoding:utf-8
'''
    Plugin para:
        * clonar compras en inventarios a almacen clon 
        * movimientos de app inventarios fisicos en vivo a almacen_clon
    
    Como Activar:
        1) Indicar en la variable [almacen_clon_id] DE ESTE ARCHIVO el id del almacen que sera el clon
        2) Activar FOLIOS AUTOMATICOS en CONCEPTO COMPRAS en inventarios
        3) Agragar este archivo a los plugins en la aplicacion
'''

from django.core import management
from django.db import connections, transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import datetime
from django.db.models import Q

from microsip_web.libs.custom_db.main import first_or_none, get_existencias_articulo
from ...libs.api.models import DocumentoCompras, ConceptosIn, Registry, Almacenes, DocumentoComprasDetalle, DoctosIn, DoctosInDet
from microsip_web.libs.inventarios import ajustes_get_or_create

almacen_clon_id = 1087990

@receiver(post_save, sender=DocumentoCompras)
def ClonarDocumentoCompras(sender, **kwargs):
    ''' Funcion para copiar un documento y cambiarle de almacen. '''

    documento_a_clonar =  kwargs.get('instance')
    
    #Al aplicar una compra
    if documento_a_clonar.tipo == 'C' and documento_a_clonar.aplicado == 'S':
        concepto_compras = ConceptosIn.objects.get( pk = 20 )
        fecha_actual = datetime.now()
        almacen = first_or_none( Almacenes.objects.filter(pk= almacen_clon_id) )
        
        entrada = DoctosIn.objects.create(
                almacen =  almacen,
                concepto = concepto_compras,
                aplicado = 'N',
                naturaleza_concepto = 'E',
                fecha = documento_a_clonar.fecha,
                sistema_origen = 'IN',
                usuario_creador = documento_a_clonar.usuario_creador,
                descripcion = 'CLON',
             )

        entrada.save()

        detalles_a_clonar = DocumentoComprasDetalle.objects.filter(documento = documento_a_clonar)

        for detalle in detalles_a_clonar:
            DoctosInDet.objects.create(
                    doctosIn = entrada,
                    almacen = almacen,
                    concepto = entrada.concepto,
                    claveArticulo = detalle.clave_articulo,
                    articulo = detalle.articulo,
                    tipo_movto = 'E',
                    unidades = detalle.unidades,
                    costo_unitario = detalle.precio_unitario,
                    costo_total = detalle.precio_total_neto,
                    metodo_costeo = 'C',
                    fecha = fecha_actual
                )

@receiver(pre_save, sender=DoctosInDet)
def ClonarExistencia(sender, **kwargs):
    ''' para en la aplicacion inventarios fisicos generar entradas y salidas en el almacen clon. '''
    almacen_clon = first_or_none( Almacenes.objects.filter(pk= almacen_clon_id) )

    detalle =  kwargs.get('instance')
    if almacen_clon and detalle.almacen != almacen_clon:

        if not almacen_clon.inventariando:
            almacen_clon.inventariando = True
            almacen_clon.inventario_conajustes =  detalle.almacen.inventario_conajustes
            almacen_clon.inventario_modifcostos =  detalle.almacen.inventario_modifcostos
            almacen_clon.save()

        entrada_clon, salida_clon = ajustes_get_or_create(almacen_id = almacen_clon.ALMACEN_ID, username = detalle.usuario_ult_modif)   
        
        old_detalle = first_or_none(DoctosInDet.objects.filter(pk=detalle.id))

        existe_en_detalles = DoctosInDet.objects.filter( 
                Q( doctosIn__concepto = 27 ) | Q( doctosIn__concepto = 38 ),
                articulo = detalle.articulo,
                almacen = detalle.almacen,
                doctosIn__descripcion = 'ES INVENTARIO',
            ).count() > 0

       
        unidades_diferencia = detalle.unidades
        
        #ajustar en primer conteo
        if detalle.almacen.inventario_conajustes and not existe_en_detalles:
            existencia_articulo = get_existencias_articulo(
                    articulo_id = detalle.articulo.id, 
                    connection_name = kwargs.get('using'), 
                    fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
                    almacen = almacen_clon, 
                )

            detalle_existencia_articulo = get_existencias_articulo(
                    articulo_id = detalle.articulo.id, 
                    connection_name = kwargs.get('using'), 
                    fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
                    almacen = detalle.almacen, 
                )            
            if detalle.tipo_movto == 'E':
                detalle_existencia_final = detalle.unidades + detalle_existencia_articulo
            elif detalle.tipo_movto == 'S':
                detalle_existencia_final = detalle_existencia_articulo - detalle.unidades
                
            unidades_diferencia = -existencia_articulo + detalle_existencia_final

        if old_detalle:
            if old_detalle.tipo_movto == 'E':
                unidades_diferencia = detalle.unidades - old_detalle.unidades
            elif old_detalle.tipo_movto == 'S':
                unidades_diferencia = (detalle.unidades - old_detalle.unidades)*-1
        else:
            if detalle.tipo_movto == 'E':
                unidades_diferencia = detalle.unidades
            elif detalle.tipo_movto == 'S':
                unidades_diferencia = detalle.unidades *-1

        
        #Entrada
        if unidades_diferencia >= 0:
            
            detalle_clon = first_or_none( DoctosInDet.objects.filter(doctosIn=entrada_clon, articulo=detalle.articulo ))     
            if detalle_clon:
                detalle_clon_unidades =detalle_clon.unidades
                detalle_clon.unidades = detalle_clon.unidades + unidades_diferencia
                detalle_clon.costo_unitario = detalle.costo_unitario
                detalle_clon.costo_total = detalle_clon.unidades * detalle_clon.costo_unitario
                detalle_clon.save()
            else:
                detalle_clon = DoctosInDet.objects.create(
                        doctosIn = entrada_clon,
                        almacen = almacen_clon,
                        concepto = entrada_clon.concepto,
                        claveArticulo = detalle.claveArticulo,
                        articulo = detalle.articulo,
                        tipo_movto = 'E',
                        unidades = unidades_diferencia,
                        costo_unitario = detalle.costo_unitario,
                        costo_total = unidades_diferencia * detalle.costo_unitario,
                        usuario_ult_modif = detalle.usuario_ult_modif
                    )

        #Salida
        elif unidades_diferencia < 0:
            detalle_clon = first_or_none( DoctosInDet.objects.filter(doctosIn=salida_clon, articulo=detalle.articulo ))
            unidades_diferencia = unidades_diferencia * -1
            
            if detalle_clon:
                detalle_clon.unidades = detalle_clon.unidades + unidades_diferencia
                detalle_clon.costo_unitario = detalle.costo_unitario
                detalle_clon.costo_total = detalle_clon.unidades * detalle_clon.costo_unitario
                detalle_clon.save()
            else:
                detalle_clon = DoctosInDet.objects.create(
                        doctosIn = salida_clon,
                        almacen = almacen_clon,
                        concepto = salida_clon.concepto,
                        claveArticulo = detalle.claveArticulo,
                        articulo = detalle.articulo,
                        tipo_movto = 'S',
                        unidades = unidades_diferencia,
                        costo_unitario = detalle.costo_unitario,
                        costo_total = unidades_diferencia * detalle.costo_unitario,
                        usuario_ult_modif = detalle.usuario_ult_modif
                    )

        c = connections[ kwargs.get('using') ].cursor()
        c.execute( "DELETE FROM SALDOS_IN where saldos_in.articulo_id = %s;"% detalle_clon.articulo.id )
        c.execute( "EXECUTE PROCEDURE RECALC_SALDOS_ART_IN %s;"% detalle_clon.articulo.id )
        transaction.commit_unless_managed()
        c.close()

        management.call_command( 'syncdb', database = kwargs.get('using') )





