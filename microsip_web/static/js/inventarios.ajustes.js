function add_existenciasarticulo_byajuste()
{
  if ( $("#enviar_btn").attr("disabled") == "disabled")
    return false
  
  if ( $('#id_unidades').val() != '' && $.isNumeric($('#id_unidades').val()) && $('#id_articulo option:selected').val() != undefined && $('#id_costo_unitario').val() != '' && $.isNumeric($('#id_costo_unitario').val()))
  { 
    Dajaxice.microsip_web.apps.inventarios.add_existenciasarticulo_byajuste(resultado,{
      'articulo_id' : $("#id_articulo").val()[0],
      'entrada_id' : $("#entrada_id").val(),
      'salida_id' : $("#salida_id").val(),
      'detalle_unidades' : $("#id_unidades").val(),
      'detalle_costo_unitario' : $("#id_costo_unitario").val(),
      }
    ); 
    
    $("#enviar_btn").attr("disabled",true);
    $("#enviar_btn").text("Enviando...");
  }
  else
  {
    
    if ($('#id_articulo option:selected').val() == undefined)
    {
      alert("El campo articulo es obligatorio");
      $("#id_articulo_text").focus();
    }
    else if ($('#id_unidades').val() == '')
    { 
      alert("El campo unidades es obligatorio");
      $("#id_unidades").focus();
    }
    else if ($.isNumeric($('#id_unidades').val()) == false )
    {
      alert("Unidades incorrectas");
      $("#id_unidades").focus();
    }
    else if ($('#id_costo_unitario').val() == '')
    { 
      alert("El campo costo unitario es obligatorio");
      $("#id_costo_unitario").focus();
    }
    else if ($.isNumeric($('#id_costo_unitario').val()) == false )
    {
      alert("Costo unitario incorrectas");
      $("#id_costo_unitario").focus();
    } 
    
  }
}

function resultado(data)
{
  window.location = "/inventarios/inventariofisico_ajustes/"+data.alamcen_id+"/";
}

function mostrar_existencias(data) 
{
  alert( data.existencias + " Articulos en existencia" );
  $('#span_alerta_unidades').html(data.existencias + ' en existencia.');
  $("#id_costo_unitario").val(data.costo_ultima_compra);
}

$('#id_claveArticulo').live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 

  if (keyCode == 13 || keyCode == 9) 
  { 
    if($("#id_claveArticulo").val() != '')
      Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(cargar_art,{'articulo_clave': $('#id_claveArticulo').val(), 'almacen': $("#almacen_nombre").val(), });
    else
      $("#id_articulo_text").focus();
    return false
  }

});


function load_localstorage()
{
  modo_rapido = localStorage.getItem("modo_rapido");
  if (modo_rapido == null)
    localStorage.setItem("modo_rapido", 'false');
  
  if(localStorage.getItem("modo_rapido") == 'true')
    $("#id_claveArticulo").focus();
  else
  {
    $("#id_articulo_text").focus();
    $("#chbx_modorapido").attr('checked', true);
  }

  $('#id_claveArticulo').focusin(function(){
    if (localStorage.getItem("modo_rapido") == 'false')
      localStorage.setItem("modo_rapido", 'true');
  });

  $('#id_articulo_text').focusin(function(){
    if (localStorage.getItem("modo_rapido") == 'true')
      localStorage.setItem("modo_rapido", 'false');
  });

  ubicacion = localStorage.getItem("ubicacion");
  if (ubicacion == null)
    localStorage.setItem("ubicacion", '');
  
  $("#id_ubicacion").val(localStorage.getItem("ubicacion"));
  $("#id_ubicacion").change(function() {
    localStorage.setItem("ubicacion",$("#id_ubicacion").val());
  });
}

function cargar_art(data)
{
  if (data.error_msg == "no_existe_clave")
  {
    var opciones = data.opciones_clave
    var html_var = "<table><tr><th>Clave</th><th>Articulo</td><tr/>"
    var no_opciones = 0
    for (art in opciones)
    { 
      no_opciones = no_opciones +  1;
      html_var = html_var + "<tr><td><a href='#' class='clave_link'>" + art + "</a></td>" + "<td>" + opciones[art] + "</td></tr>"
    }
    html_var = html_var + "</table>"
    if (no_opciones > 0)
    {
      $("#modal_opciones-claves > .modal-body").html(html_var);
      $(".clave_link").on("click",function(){
        $("#id_claveArticulo").val($(this).text());
        $("#modal_opciones-claves").modal("hide");
        Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(cargar_art,{'articulo_clave': $('#id_claveArticulo').val(), 'almacen': $("#almacen_nombre").val(), });
      });

      $("#modal_opciones-claves").modal();
    }
    else
      alert('No existe ningun articulo con la clave ['+ $("#id_claveArticulo").val() +']');
  } 
  else
  {
    cargar_articulo( data.articulo_id, data.articulo_nombre, data.existencias, data.costo_ultima_compra  );
  }
}

function cargar_articulo( articulo_id, articulo_nombre, existencias, costo_ultima_compra )
{
  $('#id_articulo-deck').attr('style','');
  $('#id_articulo-deck').html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
  $('#id_articulo').html('<option selected="selected" value="'+articulo_id+'"></option>');
  $('#id_articulo_text').hide();
  $('#span_alerta_unidades').html(existencias + ' en existencia.');
  $("#id_costo_unitario").val(costo_ultima_compra);

  $(".remove").on('click', function(){
    $('#span_alerta_unidades').html('');
    $("#id_unidades").val('');
    $(".span_clave").show();
    $(".span_articulo").hide();
    
    $("#id_claveArticulo").val(""); 
    if(localStorage.getItem("modo_rapido") == 'true')
      $("#id_claveArticulo").focus();
    else
      $("#id_articulo_text").focus();
  });

  $("#id_unidades").focus();
  alert( existencias + " Articulos en existencia" );

}

function mostrar_articulo(data){
  if (data.articulo_id != 0)
  {
    $('#id_articulo-deck').attr('style','');
    $('#id_articulo-deck').html('<span class="div hilight" data-value="'+data.articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+data.articulo_nombre+'</span>');
    $('#id_articulo').html('<option selected="selected" value="'+data.articulo_id+'"></option>');
    $('#id_articulo_text').hide();
  }
   else
  {

    $('#id_articulo_text').attr('style','');
    $('#id_articulo-deck').html('');
    $('#id_articulo').html('');
    $('#id_articulo_text').show(); 
  }
}


$("#id_articulo").change(function(){
  Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byid(mostrar_existencias,{'articulo_id': $("#id_articulo").val()[0],'almacen': $("#almacen_nombre").val(), }); 
});

if (Modernizr.localstorage) 
  load_localstorage();
else
  $("#chbx_modorapido").attr('checked', true);
// modo_rapido_ajustes = localStorage.getItem("modo_rapido_ajustes");
// if (modo_rapido_ajustes == null)
//   localStorage.setItem("modo_rapido_ajustes", 'false');

// if(localStorage.getItem("modo_rapido_ajustes") == 'true')
//   $("#id_claveArticulo").focus();
// else
//   $("#id_articulo_text").focus();

// $('#id_claveArticulo').focusin(function(){
//   if (localStorage.getItem("modo_rapido_ajustes") == 'false')
//     localStorage.setItem("modo_rapido_ajustes", 'true');

// });

// $('#id_articulo_text').focusin(function(){
//   if (localStorage.getItem("modo_rapido_ajustes") == 'true')
//     localStorage.setItem("modo_rapido_ajustes", 'false');
// });