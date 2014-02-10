var seleccionar_articulo;

function calcular_total_ventas()
{
  suma = 0; 
  $.each($("input[name*='costo_total']"), function(){
  	if ( $(this).parent().parent().attr('style') == undefined && $(this).val())
  		suma = suma + eval($(this).val());
  });
  // $("#span_total_ventas").html("<strong>Total</strong> $ " + suma);	
}



seleccionar_articulo = $("input[name*='claveArticulo']").InputClaveArticulo({
  searchFunction : Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave,
  clavecommun_name: 'claveArticulo',
  get_detailsFunction: Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid,
  load_detailsFunction: cargar_detallesarticulo
});
seleccionar_articulo = seleccionar_articulo.seleccionar_articulo;

$("input[name*='unidades'], input[name*='costo_total']").live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 
  if (keyCode == 13) 
  {
	e.preventDefault();
  }

});

$("input[name*='unidades'], input[name*='costo_unitario']").on("change", function(e) { 
  var unidades_obj = $(this).parent().parent().find("input[name*='unidades']");
  var costo_unitario_obj = $(this).parent().parent().find("input[name*='costo_unitario']");
  var costo_total_obj = $(this).parent().parent().find("input[name*='costo_total']");
  
  costo_total = unidades_obj.val() * costo_unitario_obj.val();

  costo_total_obj.val(costo_total.toFixed(2));
});



$("input[name*='costo_total']").on("change", function(e) { 
  calcular_total_ventas();
});

$("a .delete-row").on("click", calcular_total_ventas());
calcular_total_ventas();

$("input[name*='costo_total']:last").live('keydown', function(e) {
	var keyCode = e.keyCode || e.which; 
  	if (keyCode == 9 || keyCode == 13) 
  	{
		$(this).parent().parent().parent().find('a:last').click();
		// $("input[name*='claveArticulo']:last")[0].focus();	
  	}
});

function cargar_detallesarticulo(data)
{
	if (data.articulo_seguimiento == 'S')
		alert("articulo con serie no soportado");

	var costo_unitario = $("input[name='"+data.comun_name+"costo_unitario']"); 
	var unidades = $("input[name='"+data.comun_name+"unidades']");
	var input_clavearticulo = $("input[name='"+data.comun_name+"claveArticulo']"); 
	var input_costototal = $("input[name='"+data.comun_name+"costo_total']"); 
	input_clavearticulo.val(data.articulo_clave);

	costo_unitario.val(data.articulo_costoultimacompra);
	input_costototal.val(data.articulo_costoultimacompra);
	unidades.val(1);
	unidades.select();
}

$("select[name*='articulo']").change(function(){

	var comun_name = $(this).attr('name').replace("articulo", "");
	var articulo_id = $(this).find("option:selected").val();
	
	if (articulo_id != undefined)
	{
		var clave_articulo = $("input[name='"+comun_name+"claveArticulo']").val();
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
		$("input[name*='claveArticulo']:last")[0].focus();	
  	}
	
});

$("input[id*='fecha']").datepicker({dateFormat:'dd/mm/yy',});



