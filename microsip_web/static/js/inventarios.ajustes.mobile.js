function limpiarForm()
{
  $("#id_unidades, #id_claveArticulo, #id_articulo_text #id_costo_unitario").val('');
  $("#span_alerta_unidades").html("");
  $("#buscar_btn, .span_clave").show();
  $(".span_unidades, #cancelar_btn, #span_ya_ajustado, #span_sin_ajustado").hide();
  $("#enviar_btn").attr("disabled",false);
  $("#enviar_btn").text("Enviar");

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

function deselecionarArticulo()
{
  // Call Widget.deselectChoice when .remove is clicked  
  var $remove_btn = $('.autocomplete-light-widget .deck .remove')
  var widget = $($remove_btn).parents('.autocomplete-light-widget').yourlabsWidget();

  var selector = widget.input.yourlabsAutocomplete().choiceSelector;
  var choice = $($remove_btn).parents(selector);
  widget.deselectChoice(choice);
}


$(document).ready(function(){
  
  $("#id_articulo_text").before("<span class='add-on' id='span_nombre_articulo'>Nombre</span>");
  $("#id_costo_unitario").hide();
  limpiarForm();
});