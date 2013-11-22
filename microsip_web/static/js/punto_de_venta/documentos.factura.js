function cargar_factura_global(data){
	// alert(data.detalles);
	// var detallesj = JSON.stringify(eval("(" + data.detalles + ")"));
  if (data.message != '') 
  {
    alert(data.message);
  }
  else
    window.location = "/punto_de_venta/facturas/";
	// for (var i = 0; i <= data.length ; i++) 

}

$(function() {
  $("#check_almacen").on("click", function(){
    if ($("#check_almacen").attr("checked"))
      $("#id_almacen").attr("disabled",false);
    else
      $("#id_almacen").attr("disabled",true);
  });
  $("input[id*='fecha']").datepicker({dateFormat:'dd/mm/yy',});
  $('#id_doctosIn_table tbody tr').formset({
    prefix: '{{ formset.prefix }}',
    addCssClass:'btn',
    addText:'Nuevo Articulo',
    deleteText:'',
  });
  $("input[name*='clave_articulo']:last")[0].focus();  

  $("#btn_facturaglobal").on("click", function(){
    var almacen_id = null;
    if ($("#check_almacen").attr("checked"))
      almacen_id = $("#id_almacen").val();

    Dajaxice.microsip_web.apps.punto_de_venta.generar_factura_global( cargar_factura_global, { 
  		'fecha_inicio': $("#id_fecha_inicio").val(),
  	 	'fecha_fin': $("#id_fecha_fin").val(),
      'almacen_id': almacen_id,
	  });
  });
});

