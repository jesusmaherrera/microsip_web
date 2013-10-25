function limpiarForm()
{
  $("#id_unidades, #id_claveArticulo, #id_articulo_text").val('');
  $("#span_alerta_unidades").html("");
  $("#buscar_btn, .span_clave").show();
  $(".span_unidades, #cancelar_btn").hide();
  if ($("#chbx_modorapido").is(':checked'))
  {
    $(".span_articulo, #span_nombre_articulo").hide();
    $(".span_clave").show();
    $("#id_claveArticulo").focus();
  }
  else
  {
    if ( $("#id_articulo-deck").children().length != 0) 
      deselecionarArticulo();

    $(".span_clave").hide();
    $(".span_articulo, #id_articulo_text, #span_nombre_articulo").show();
    $("#id_articulo-text").focus();
  }
}

$(document).ready(function(){
  
  $("#id_articulo_text").before("<span class='add-on' id='span_nombre_articulo'>Nombre</span>");
  $("#id_costo_unitario").hide();
  limpiarForm();
});