function cargar_factura_global(data){
	// alert(data.detalles);
	// var detallesj = JSON.stringify(eval("(" + data.detalles + ")"));
	alert(data.detalles);
	// for (var i = 0; i <= data.length ; i++) 

}

$(function() {
  $("input[id*='fecha']").datepicker({dateFormat:'dd/mm/yy',});
  $('#id_doctosIn_table tbody tr').formset({
    prefix: '{{ formset.prefix }}',
    addCssClass:'btn',
    addText:'Nuevo Articulo',
    deleteText:'',
  });
  $("input[name*='clave_articulo']:last")[0].focus();  

  $("#btn_facturaglobal").on("click", function(){
  	Dajaxice.microsip_web.apps.punto_de_venta.generar_factura_global( cargar_factura_global, { 
		'fecha_inicio': $("#id_fecha_inicio").val(),
		'fecha_fin': $("#id_fecha_fin").val(),
	});
  });
});

