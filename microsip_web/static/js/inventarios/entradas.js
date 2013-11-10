

function calcular_total_ventas()
{
  suma = 0; 
  $.each($("input[name*='costo_total']"), function(){
  	if ( $(this).parent().parent().attr('style') == undefined && $(this).val())
  		suma = suma + eval($(this).val());
  });
  // $("#span_total_ventas").html("<strong>Total</strong> $ " + suma);	
}


function seleccionar_articulo(data)
{	
	if (data.articulo_id != '')
	{
		var articulo = $("select[name='"+data.comun_name+"articulo']");
		var deck_selector = articulo.parent().find(".deck");
		var articulo_text = $("input[name='"+data.comun_name+"articulo-autocomplete']");

		deck_selector.attr('style','');
		deck_selector.html('<span class="div hilight" data-value="'+data.articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+data.articulo_nombre+'</span>');
		articulo.html('<option selected="selected" value="'+data.articulo_id+'"></option>');
		articulo_text.hide();
	}
	else
	{
		var opciones = data.opciones_clave;
		var clave_articulo = $("input[name='"+data.comun_name+"claveArticulo']");
		var no_opciones = 0;
		html_var = '';
		for (art in opciones)
		{ 
		  no_opciones = no_opciones +  1;
		  html_var = html_var + "<a href='#' class='clave_link'>" + art + "</a> " + opciones[art]+"<br>";
		}
		if (no_opciones > 0)
		{
		  $("#div_filterclaves").html(html_var);
		  $(".clave_link").on("click",function(){
		    clave_articulo.val($(this).text());
		    $("#modal_opciones-claves").modal("hide");
		    var clave = clave_articulo.val();
		    var comun_name = data.comun_name;
		    get_articulo_byclave(clave, comun_name);
		  });
		  $("#modal_opciones-claves").modal();
		}
		else
		  alert('No existe ningun articulo con la clave ['+ clave_articulo.val() +']');
	}

	if (data.articulo_id != '')
	{
		var clave_articulo = $("input[name='"+data.comun_name+"claveArticulo']");

		Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid( cargar_detallesarticulo, { 
				'articulo_id': data.articulo_id,
				'comun_name': data.comun_name,
				'articulo_clave': clave_articulo.val(),
			} 
		);
	}
}

function get_articulo_byclave(clave, comun_name)
{	
	if( clave != '' )
	  Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave( seleccionar_articulo , { 'clave': clave, 'comun_name': comun_name,} );
}

$("input[name*='claveArticulo']").live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 
  
  var clave = $(this).val();

  var comun_name = $(this).attr('name').replace("claveArticulo", "");

  if (keyCode == 13 || keyCode == 9) 
  {
    get_articulo_byclave(clave, comun_name);
    if (keyCode == 13 )
		e.preventDefault();
  }

});

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

  costo_total_obj.val(costo_total);
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
	input_clavearticulo.val(data.articulo_clave);

	costo_unitario.val(data.articulo_costoultimacompra)
	unidades.val('');
	unidades.focus();
}


$("select[name*='articulo']").change(function(){

	var comun_name = $(this).attr('name').replace("articulo", "");
	var articulo_id = $(this).find("option:selected").val();
	
	if (articulo_id != undefined)
	{
		Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid( cargar_detallesarticulo, { 
				'articulo_id': articulo_id,
				'comun_name': comun_name,
				'articulo_clave':'',
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



