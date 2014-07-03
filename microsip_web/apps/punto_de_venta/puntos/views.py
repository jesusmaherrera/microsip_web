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

@login_required(login_url='/login/')
def inicializar_puntos_articulos(request):
    basedatos_activa = request.session['selected_database']
    if basedatos_activa == '':
        return HttpResponseRedirect('/select_db/')

    Articulo.objects.update(puntos=None, dinero_electronico=None, hereda_puntos=1)
    LineaArticulos.objects.update(puntos=None, dinero_electronico=None, hereda_puntos=1)
    GrupoLineas.objects.update(puntos=None, dinero_electronico=None)
    
    return HttpResponseRedirect('/punto_de_venta/articulos/')

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

        claves = []

        #Datos para cliente
        rolclaves = ClienteClaveRol.objects.get( es_ppal = 'S' )
        moneda_local = Moneda.objects.get( es_moneda_local = 'S' )
        
        try:
            condicion_pago = CondicionPago.objects.get( es_predet = 'S' )
        except ObjectDoesNotExist:
            condicion_pago = CondicionPago.objects.all()[0]
        
        try:            
            tipo_cliente = ClienteTipo.objects.get( nombre = 'TARJETA PROMOCION' )
        except ObjectDoesNotExist:
            tipo_cliente = ClienteTipo.objects.create(id=-1, nombre = 'TARJETA PROMOCION', valor_puntos = 1)

        # Datos generales
        cliente_eventual = Cliente.objects.get(pk=Registry.objects.get(nombre='CLIENTE_EVENTUAL_PV_ID').get_value())
        articulo = Articulo.objects.get(pk=Registry.objects.get(nombre='ARTICULO_VENTAS_FG_PV_ID').get_value())
        
        cajero = Cajero.objects.exclude(operar_cajas='N')[0]

        if cajero.operar_cajas =='T':
            caja_id = Caja.objects.all().values_list( 'caja__id', flat = True )[0]
        else:
            caja_id = CajeroCaja.objects.filter(cajero=cajero).values_list( 'caja__id', flat = True )[0]
        caja = Caja.objects.get(pk=caja_id)


        forma_cobro_efectivo = FormaCobro.objects.filter(tipo='E')[0]
        impuesto_al_0 = Impuesto.objects.filter(tipo_iva='3')[0]

        #RESTRICCIONES
        # ariculos, cliente eventual indicado, cajero que opere cajas, forma de cobro efectivo primera impuesto al cero

        documentos = []
        for numero in range( iniciar_en, iniciar_en + cantidad ):
            clave = '%s%s'% ( prefijo, ( "%09d" % numero ) )

            cliente = Cliente.objects.create(
                id = next_id( 'ID_CATALOGOS', connection_name ), 
                nombre = clave, 
                moneda = moneda_local, 
                condicion_de_pago = condicion_pago, 
                tipo_cliente = tipo_cliente,
                tipo_tarjeta = tipo_tarjeta,
                hereda_valorpuntos = hereda_valorpuntos,
                valor_puntos = valor_puntos,
                hereda_puntos_a = cliente_eventual,
                )

            ClienteClave.objects.create( id = -1, clave = clave, cliente = cliente, rol =  rolclaves )

            #si hay puntos extra
            if puntos>0 or dinero_electronico > 0:
                
                documento = PuntoVentaDocumento.objects.create(
                    id = -1,
                    #los primeros que encuentre
                    caja = caja,
                    cajero = cajero,
                    cliente = cliente_eventual,
                    #primero que encuentre
                    almacen = caja.almacen,
                    moneda = cliente.moneda,
                    tipo = 'V',
                    fecha = datetime.now(),
                    hora = datetime.now().strftime('%H:%M:%S'),
                    clave_cliente = clave,
                    tipo_cambio = 1,
                    aplicado = 'N',
                    importe_neto = 0.01,
                    total_impuestos = 0,
                    importe_donativo = 0,
                    total_fpgc = 0,
                    descripcion = 'PARA APLICAR PUNTOS EXTRA',
                    usuario_creador = request.user.username,
                    #DE APP PUNTOS
                    puntos = puntos,
                    dinero_electronico = dinero_electronico,
                    cliente_tarjeta = cliente,
                )
                
                PuntoVentaDocumentoDetalle.objects.create(
                    id =-1,
                    documento_pv = documento,            
                    articulo = articulo, 
                    unidades =1,                
                    unidades_dev =0,            
                    precio_unitario  = 0.01,      
                    precio_unitario_impto = 0.0116,   
                    fpgc_unitario  =0,         
                    porcentaje_descuento =0,
                    precio_total_neto =0.01,     
                    porcentaje_comis =0,       
                    rol = 'N',                     
                    posicion = 1,
                    puntos = puntos,
                    dinero_electronico = dinero_electronico,
                )
                
                PuntoVentaCobro.objects.create(
                    id=-1,
                    tipo='C',
                    documento_pv= documento,
                    forma_cobro=forma_cobro_efectivo,
                    importe=0.01,
                    tipo_cambio=1,
                    importe_mon_doc=0.01,
                )

                c = connections[connection_name].cursor()
                query =  '''INSERT INTO impuestos_doctos_pv (docto_pv_id, impuesto_id, venta_neta, otros_impuestos, pctje_impuesto, importe_impuesto) \
                    VALUES (%s, %s, 0.01, 0, 0, 0)'''
                c.execute(query,[documento.id,  int(impuesto_al_0.id),])
                c.close()
                
                documentos.append(documento)
                
        management.call_command( 'syncdb', database = connection_name, interactive= False)

        for doc in documentos:
            doc.aplicado='S'
            doc.save()

        management.call_command( 'syncdb', database = connection_name, interactive= False)

        msg = 'Clientes generados correctamente.'
        form = generartarjetas_form()

    c= { 'form' : form, 'msg' : msg, }
    return render_to_response( template_name, c, context_instance = RequestContext( request ) )