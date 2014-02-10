var seleccionar_articulo;

function calcular_total_ventas()
{
  suma = 0; 
  $.each($("input[name*='precio_total_neto']"), function(){
  	if ( $(this).parent().parent().attr('style') == undefined && $(this).val())
  		suma = suma + eval($(this).val());
  });
  // $("#span_total_ventas").html("<strong>Total</strong> $ " + suma);	
}



seleccionar_articulo = $("input[name*='clave_articulo']").InputClaveArticulo({
  searchFunction : Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave,
  clavecommun_name: 'clave_articulo',
  get_detailsFunction: Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid,
  load_detailsFunction: cargar_detallesarticulo
});
seleccionar_articulo = seleccionar_articulo.seleccionar_articulo;

$("input[name*='unidades'], input[name*='precio_total_neto']").live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 
  if (keyCode == 13) 
  {
	e.preventDefault();
  }

});

$("input[name*='unidades'], input[name*='precio_unitario']").on("change", function(e) { 
  var unidades_obj = $(this).parent().parent().find("input[name*='unidades']");
  var costo_unitario_obj = $(this).parent().parent().find("input[name*='precio_unitario']");
  var costo_total_obj = $(this).parent().parent().find("input[name*='precio_total_neto']");
  
  precio_total_neto = unidades_obj.val() * costo_unitario_obj.val();

  costo_total_obj.val(precio_total_neto.toFixed(2));
});



$("input[name*='precio_total_neto']").on("change", function(e) { 
  calcular_total_ventas();
});

$("a .delete-row").on("click", calcular_total_ventas());
calcular_total_ventas();

$("input[name*='precio_total_neto']:last").live('keydown', function(e) {
	var keyCode = e.keyCode || e.which; 
  	if (keyCode == 9 || keyCode == 13) 
  	{
		$(this).parent().parent().parent().find('a:last').click();
		// $("input[name*='clave_articulo']:last")[0].focus();	
  	}
});

function cargar_detallesarticulo(data)
{
	if (data.articulo_seguimiento == 'S')
		alert("articulo con serie no soportado");

	var precio_unitario = $("input[name='"+data.comun_name+"precio_unitario']"); 
	var unidades = $("input[name='"+data.comun_name+"unidades']");
	var input_clavearticulo = $("input[name='"+data.comun_name+"clave_articulo']"); 
	var input_costototal = $("input[name='"+data.comun_name+"precio_total_neto']"); 
	input_clavearticulo.val(data.articulo_clave);

	precio_unitario.val(data.articulo_costoultimacompra);
	input_costototal.val(data.articulo_costoultimacompra);
	unidades.val(1);
	unidades.select();
}

$("select[name*='articulo']").change(function(){

	var comun_name = $(this).attr('name').replace("articulo", "");
	var articulo_id = $(this).find("option:selected").val();
	
	if (articulo_id != undefined)
	{
		var clave_articulo = $("input[name='"+comun_name+"clave_articulo']").val();
		Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid( cargar_detallesarticulo, { 
				'articulo_id': articulo_id,
				'comun_name': comun_name,
				'articulo_clave':clave_articulo,
			} 
		);
	}	
});  

$("input[name*='unidades']:last").live('keydown', function(e) {
	var keyCode = e.keyCode || e.which; 
  	if (keyCode == 13) 
  	{
		$(this).parent().parent().parent().find('a:last').click();
		$("input[name*='clave_articulo']:last")[0].focus();	
  	}
	
});

$("input[id*='fecha']").datepicker({dateFormat:'dd/mm/yy',});






