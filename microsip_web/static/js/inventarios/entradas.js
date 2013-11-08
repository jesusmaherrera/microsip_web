
function seleccionar_articulo(data)
{	

	if (data.articulo_id != '')
	{
		var deck_selector = $('#'+data.comun_id+'articulo-deck');
		var articulo = $('#'+data.comun_id+'articulo');
		var articulo_text = $('#'+data.comun_id+'articulo_text');
		var costo_unitario = $('#'+data.comun_id+'costo_unitario');
		var unidades = $('#'+data.comun_id+'unidades');

		deck_selector.attr('style','');
		deck_selector.html('<span class="div hilight" data-value="'+data.articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+data.articulo_nombre+'</span>');
		articulo.html('<option selected="selected" value="'+data.articulo_id+'"></option>');
		articulo_text.hide();
		costo_unitario.val(data.articulo_costoultimacompra)
		unidades.val('');
		unidades.focus();
	}
	else
	{
		var opciones = data.opciones_clave;
		var clave_articulo = $('#'+data.comun_id+'claveArticulo');
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
		    var comun_id = data.comun_id;
		    get_articulo_byclave(clave, comun_id);
		  });
		  $("#modal_opciones-claves").modal();
		}
		else
		  alert('No existe ningun articulo con la clave ['+ clave_articulo.val() +']');
	}
}

function get_articulo_byclave(clave, comun_id)
{	
	if( clave != '' )
	  Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave( seleccionar_articulo , { 'clave': clave, 'comun_id': comun_id,} );
}

$("input[name*='claveArticulo']").live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 
  
  var clave = $(this).val();
  var comun_id = $(this).attr('id').replace("claveArticulo", "");

  if (keyCode == 13 || keyCode == 9) 
  {
    get_articulo_byclave(clave, comun_id);
    if (keyCode == 13 )
		e.preventDefault();
  }

});

$("input[name*='unidades']").live('keydown', function(e) { 
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