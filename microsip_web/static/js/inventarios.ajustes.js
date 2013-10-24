function add_existenciasarticulo_byajuste()
{

  if ( $('#id_unidades').val() != '' && $.isNumeric($('#id_unidades').val()) && $('#id_articulo option:selected').val() != undefined && ( ( $('#puede_modificar_costos').val() == 'True'  && $('#id_costo_unitario').val() != '' && $.isNumeric($('#id_costo_unitario').val()) == true)  || ($('#puede_modificar_costos').val() == 'False') ) ) 
  { 
    var costo_unitario = 0
    if ( $('#puede_modificar_costos').val() == 'True' )
      costo_unitario = $("#id_costo_unitario").val()
    Dajaxice.microsip_web.apps.inventarios.add_existenciasarticulo_byajustes_view(resultado,{
      'ubicacion' : $("#id_ubicacion").val(),
      'articulo_id' : $("#id_articulo").val()[0],
      'entrada_id' : $("#entrada_id").val(),
      'salida_id' : $("#salida_id").val(),
      'detalle_unidades' : $("#id_unidades").val(),
      'detalle_costo_unitario' :costo_unitario,
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
      alert("Costo unitario incorrectO");
      $("#id_costo_unitario").focus();
    }
    
  }
}

function agregar_articulos_porlineafn()
{
  if ( $("#btn_agregar_articulosinexistencia_bylinea").attr("disabled") == "disabled")
    return false

  var linea = $("#id_linea").val();
  if (linea == '') 
    alert('Por favor seleccione una linea');
  else
  {
    Dajaxice.microsip_web.apps.inventarios.add_articulossinexistencia_bylinea(mostrar_articulos_agregados,{
        'ubicacion' : $("#id_ubicacion").val(),
        'linea_id' : linea,
        'entrada_id' : $("#entrada_id").val(),
        'salida_id' : $("#salida_id").val(),
      });

    $('#btn_agregar_articulosinexistencia_bylinea').hide();
    $('#btnCancel').hide();
    $("#btn_agregar_articulosinexistencia_bylinea").attr("disabled",true);
    $("#id_agregando_span").show();
  }
}

function alert_resultado(data)
{
  alert(data.mensaje);
  window.location = "/inventarios/almacenes/";
}

function cerrar_inventario()
{
  Dajaxice.microsip_web.apps.inventarios.close_inventario_byalmacen_view(alert_resultado,{
    'almacen_id' : $("#almacen_id").val(),
  });
}

function agregar_articulos_fn()
{
  if ( $("#btn_agregar_articulosinexistencia").attr("disabled") == "disabled")
    return false

  Dajaxice.microsip_web.apps.inventarios.add_articulossinexistencia(mostrar_articulos_agregados,{
    'ubicacion' : $("#id_ubicacion").val(),
    'entrada_id' : $("#entrada_id").val(),
    'salida_id' : $("#salida_id").val(),
  });

  $('#btn_agregar_articulosinexistencia').hide();
  $('#btnCancel').hide();
  $("#btn_agregar_articulosinexistencia").attr("disabled",true);
  $("#id_agregando_span_all").show();
}

function mostrar_articulos_agregados(data)
{
  if (data.articulos_agregados > 0)
  {
    mensaje ='Se agregaron '+ data.articulos_agregados+ ' Articulos'
    if (data.articulo_pendientes > 0)
      mensaje = 'La aplicacion solo genero ' + data.articulos_agregados+ ' Articulos, faltaron de generar '+data.articulo_pendientes + ' Articulos.'
    alert(mensaje);
    window.location = "/inventarios/inventariofisico_ajustes/" + $( "#almacen_id" ).val() + "/";
  }
  else
    alert('No hay articulos por inicializar');
  
  // if (!Modernizr.localstorage) 
  //   window.location = "/inventarios/inventariofisico/{{ inventario_id }}/1/";
  // else
  //   window.location = "/inventarios/inventariofisico/{{ inventario_id }}/" + localStorage.getItem("dua") + "/";
}

function resultado(data)
{
  window.location = "/inventarios/inventariofisico_ajustes/"+data.alamcen_id+"/";
}

function mostrar_existencias(data) 
{
  mostrar_spans(data.ya_ajustado);
  $('#span_alerta_unidades').html(data.existencias + " en existencia. <a tabindex='-1' href='#modal_movimientos_articulo' role='button' data-toggle='modal'><i class='icon-info-sign icon-white'></i></a> ");

  var entradas = data.detalle_modificacionestime.split(',');
  var salidas = data.detalle_modificacionestime_salidas.split(',');
  
  var entradas_html = '<h5> ENTRADAS: </h5>';
  
  $.each(entradas, function(key, entrada) {
    numero = key + 1;
    if (entrada != "")
      entradas_html = entradas_html + numero + ") " + entrada + '<br>';
  });

  entradas_html = entradas_html + '<h5> SALIDAS: </h5>';
  
  $.each(salidas, function(key, salida) {
    numero = key + 1;
    if (salida != "")
      entradas_html = entradas_html + numero + ") " + salida + '<br>';
  });

  $("#modal_movimientos_articulo > .modal-body").html(entradas_html);

  $("#id_costo_unitario").val(data.costo_ultima_compra);
}

$(".btn-info-inventario").on("click", function(){
  Dajaxice.microsip_web.apps.inventarios.get_detallesArticuloenInventario(mostrar_detalle,{'detalle_invfis_id': $(this).parent().find("input[name='detalle_id']").val(),});
});

$('#id_claveArticulo').live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 

  if (keyCode == 13 || keyCode == 9) 
  { 
    if($("#id_claveArticulo").val() != '')
      Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(cargar_art,{
        'articulo_clave': $('#id_claveArticulo').val(), 
        'almacen': $("#almacen_nombre").val(), 
        'entrada_id' : $("#entrada_id").val(),
      });
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
        Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(cargar_art,{
          'articulo_clave': $('#id_claveArticulo').val(), 
          'almacen': $("#almacen_nombre").val(), 
          'entrada_id' : $("#entrada_id").val(),
        });
      });

      $("#modal_opciones-claves").modal();
    }
    else
      alert('No existe ningun articulo con la clave ['+ $("#id_claveArticulo").val() +']');
  } 
  else
  {
    cargar_articulo( data.articulo_id, data.articulo_nombre, data.existencias, data.costo_ultima_compra, data.detalle_modificacionestime, data.ya_ajustado, data.detalle_modificacionestime_salidas);
  }
}

function mostrar_spans(ya_ajustado)
{
  if (ya_ajustado == true)
  {
    $('#span_alerta_unidades, #span_ya_ajustado').show();
    $('#span_sin_ajustado').hide();
  }
  else
  {  
    $('#span_alerta_unidades, #span_sin_ajustado').show();
    $('#span_ya_ajustado').hide();
  }
}

function cargar_articulo( articulo_id, articulo_nombre, existencias, costo_ultima_compra, detalle_modificacionestime, ya_ajustado, detalle_modificacionestime_salidas )
{
  $('#id_articulo-deck').attr('style','');
  $('#id_articulo-deck').html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
  $('#id_articulo').html('<option selected="selected" value="'+articulo_id+'"></option>');
  $('#id_articulo_text').hide();
  
  mostrar_spans(ya_ajustado);

  $('#span_alerta_unidades').html(existencias + " en existencia. <a tabindex='-1' href='#modal_movimientos_articulo' role='button' data-toggle='modal'><i class='icon-info-sign icon-white'></i></a> ");
  
  var entradas = detalle_modificacionestime.split(',');
  var salidas = detalle_modificacionestime_salidas.split(',');
  
  var entradas_html = '<h5> ENTRADAS: </h5>';
  
  $.each(entradas, function(key, entrada) {
    numero = key + 1;
    if (entrada != "")
      entradas_html = entradas_html + numero + ") " + entrada + '<br>';
  });

  entradas_html = entradas_html + '<h5> SALIDAS: </h5>';
  
  $.each(salidas, function(key, salida) {
    numero = key + 1;
    if (salida != "")
      entradas_html = entradas_html + numero + ") " + salida + '<br>';
  });
  $("#modal_movimientos_articulo > .modal-body").html(entradas_html);

  $("#id_costo_unitario").val(costo_ultima_compra);

  $(".remove").on('click', function(){
    $('#span_alerta_unidades').html('');
    $('#span_alerta_unidades, #span_ya_ajustado, #span_sin_ajustado').hide();
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
  if( $("#id_articulo").val() == null )
  {
    $('#span_alerta_unidades, #span_ya_ajustado, #span_sin_ajustado').hide();
    $('#id_costo_unitario').val('');
    $("#id_articulo_text").focus();
  }
  else
  {
    Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byid(mostrar_existencias,{
      'articulo_id': $("#id_articulo").val()[0],
      'almacen': $("#almacen_nombre").val(), 
      'entrada_id' : $("#entrada_id").val(),
    }); 
  }
});

$('#span_alerta_unidades, #span_ya_ajustado, #span_sin_ajustado').hide();

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