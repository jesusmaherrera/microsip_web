var seleccionar_articulo;

function cargar_factura_global(data){
	// alert(data.detalles);
	// var detallesj = JSON.stringify(eval("(" + data.detalles + ")"));
  if (data.message != '') 
  {
    alert(data.message);
  }
  else
  {
    $.each(data.detalles, function( index, detalle ) {
      seleccionar_articulo({'articulo_id':detalle.articulo_id, 'articulo_nombre':detalle.articulo_nombre, 'comun_name':'docto_pv_det_set-'+index+'-'});
      $("input[name='docto_pv_det_set-"+index+"-unidades']").val(detalle.unidades);
      $("input[name='docto_pv_det_set-"+index+"-precio_unitario']").val(detalle.precio);
      $("input[name='docto_pv_det_set-"+index+"-precio_total_neto']").val(detalle.precio_total_neto);
      $("input[name='docto_pv_det_set-"+index+"-clave_articulo']").val(detalle.articulo_clave);
      $("input[name='docto_pv_det_set-"+index+"-porcentaje_descuento']").val(detalle.porcentaje_descuento);
      $("input[name='docto_pv_det_set-"+index+"-detalles_liga']").val(detalle.detalles_relacion);
      if (data.detalles.length-1 > index)
        $('#id_doctosIn_table').find('a:last').click();
    });
    
    $("#id_importe_neto").val(data.totales.importe_neto);
    $("#id_total_impuestos").val(data.totales.total_impuestos).trigger('change');
    $("#id_importe_donativo").val(data.totales.importe_donativo);
    $("#id_total_fpgc").val(data.totales.total_fpgc);
    $("#id_importe_descuento").val(data.totales.importe_descuento);
    $("#id_ventas_en_factura").val(data.totales.ventas_facturadas);
    
    
    var venta_neta = '';
    var otros_impuestos = '';
    var  importe_impuesto = '';
    var impuestos_ids = "";
    var porcentaje_impuestos = "";

    $.each(data.impuestos, function( index, impuesto ) {
      venta_neta = venta_neta + impuesto.venta_neta  + ","
      otros_impuestos = otros_impuestos + impuesto.otros_impuestos  + ","
      importe_impuesto = importe_impuesto + impuesto.importe_impuesto  + ","
      impuestos_ids = impuestos_ids + impuesto.impuestos_ids  + ","
      porcentaje_impuestos = porcentaje_impuestos + impuesto.porcentaje_impuestos  + ","
    });

    $("#id_impuestos_venta_neta").val(venta_neta);
    $("#id_impuestos_otros_impuestos").val(otros_impuestos);
    $("#id_impuestos_importe_impuesto").val(importe_impuesto);
    $("#id_impuestos_ids").val(impuestos_ids);
    $("#id_impuestos_porcentaje_impuestos").val(porcentaje_impuestos);
    
    
    $("#id_descripcion").val("FACTURA GLOBAL("+data.fecha_inicio+"-"+data.fecha_fin+")");

    var ventas_ids = '';
    $.each(data.ventas_facturadas, function( index, venta ) {
      ventas_ids = $("#id_ventas_en_factura").val() + venta.id;
      if (data.ventas_facturadas.length-1 > index)
        ventas_ids = ventas_ids +',';

      $("#id_ventas_en_factura").val(ventas_ids);    
      $("#ligas_fromset tbody").append('<tr><td><p class="text-right">'+venta.fecha+'</p></td><td><p class="text-right">'+ venta.folio+'</p></td><td><p class="text-right">'+ venta.importe_neto+'</p></td></tr>');
    });
    // ligas_fromset
    $("#id_total_ventas").text(data.ventas_facturadas.length+" ventas de mostrador");
    $('#modal_factura_global').modal("hide");
  }
}

$(function() {
  var importe_neto = $("#id_importe_neto").val();
  var total_impuestos = $("#id_total_impuestos").val();
  var total = parseFloat(importe_neto) + parseFloat(total_impuestos);
  $("#label_total_impuestos").text(total_impuestos);
  $("#label_importe_neto").text(importe_neto);
  $("#label_total").text(total.toFixed(2));
  
  $("#id_total_impuestos").change(function(){
    $("#label_total_impuestos").text($("#id_total_impuestos").val());
    $("#label_importe_neto").text($("#id_importe_neto").val());
  });

  seleccionar_articulo = $("input[name*='clave_articulo']").InputClaveArticulo({
    searchFunction : Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave
  });

  seleccionar_articulo = seleccionar_articulo.seleccionar_articulo;

  /*Para agregar nuevos renglones*/
  // $("input[name*='precio_total_neto']:last").live('keydown', function(e) {
  //   var keyCode = e.keyCode || e.which; 
  //     if (keyCode == 9 || keyCode == 13) 
  //     {
  //       $(this).parent().parent().parent().find('a:last').click();
  //       $("input[name*='clave_articulo']").InputClaveArticulo({
  //         searchFunction : Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave
  //       });
  //     }
  // });

  $("#check_almacen").on("click", function(){
    if ($("#check_almacen").attr("checked"))
      $("#id_almacen").attr("disabled",false);
    else
      $("#id_almacen").attr("disabled",true);
  });
  $("input[id*='fecha']").datepicker({dateFormat:'dd/mm/yy',});
  
  $("#id_cliente_text").focus();
  // $("input[name*='clave_articulo']:last")[0].focus();  

  $("#btn_facturaglobal").on("click", function(){

    almacen_id = $("#id_almacen").val();
    if ($("#check_almacen").attr("checked") && almacen_id == '') {
        alert('Seleciona un almacen');
        return false
    }
    else
      almacen_id = null;
    
    if ($("#id_fecha_inicio").val() == "")
    {
      alert('Indica una fecha por favor');
      return false 
    }

    if ($("#id_cliente").val() == null)
    {
      alert('Seleciona el cliente');
      return false 
    }
    
     // window.location = "/punto_de_venta/facturaglobal/"+$("#id_cliente").val()[0]+"/"+$("#id_tipo").val()+"/"+$("#id_modalidad_facturacion").val()+"/";

    Dajaxice.microsip_web.apps.punto_de_venta.generar_factura_global( cargar_factura_global, { 
  		'fecha_inicio': $("#id_fecha_inicio").val(),
  	 	'fecha_fin': $("#id_fecha_fin").val(),
      'almacen_id': almacen_id,
      'cliente_id':$("#id_cliente").val()[0],
      'modalidad_facturacion': $("#id_modalidad_facturacion").val(),
      'factura_tipo': $("#id_tipo").val(),
	  });
  });
});

