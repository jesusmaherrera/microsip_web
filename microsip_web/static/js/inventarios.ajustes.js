
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

/* Inicializar articulos */

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
  }
  else
    alert('No hay articulos por inicializar');

  window.location = "/inventarios/inventariofisico/" + $( "#almacen_id" ).val() + "/";
  
  // if (!Modernizr.localstorage) 
  //   window.location = "/inventarios/inventariofisico/{{ inventario_id }}/1/";
  // else
  //   window.location = "/inventarios/inventariofisico/{{ inventario_id }}/" + localStorage.getItem("dua") + "/";
}

/* Modificar existencias */
function add_existenciasarticulo_byajuste()
{

  if ($('#id_ubicacion').val() == '')
  {
    alert("El campo ubicacion es obligatorio");
    $("#id_ubicacion").focus();
    return;
  }
  else if ($('#id_articulo option:selected').val() == undefined)
  {
    alert("El campo articulo es obligatorio");
    $("#id_articulo_text").focus();
    return;
  }
  else if ($('#id_unidades').val() == '')
  { 
    alert("El campo unidades es obligatorio");
    $("#id_unidades").focus();
    return;
  }
  else if ($.isNumeric($('#id_unidades').val()) == false )
  {
    alert("Unidades incorrectas");
    $("#id_unidades").focus();
    return;
  }
  

  if ( $("#articulo_seguimiento").val() == 'S' )
  {
    var inputs_html = ''
    for ( x = 1; x <= $('#id_unidades').val() ; x++ )
    { 
      inputs_html = inputs_html + "<input class='input-small' id='id_numeroserie_" + x + "' type='text'/> </br>";
    }   
    $("#table_numeros_serie > tbody").html(inputs_html);
    $("#modal_series").modal();

    return;
  }

  if ( ( $('#puede_modificar_costos').val() == 'True'  && $('#id_costo_unitario').val() != '' && $.isNumeric($('#id_costo_unitario').val()) == true)  || ($('#puede_modificar_costos').val() == 'False') )
  { 
    var costo_unitario = 0;
    if ( $('#puede_modificar_costos').val() == 'True' )
      costo_unitario = $("#id_costo_unitario").val();
    Dajaxice.microsip_web.apps.inventarios.add_existenciasarticulo_byajustes_view(resultado,{
      'ubicacion' : $("#id_ubicacion").val(),
      'articulo_id' : $("#id_articulo").val()[0],
      'entrada_id' : $("#entrada_id").val(),
      'salida_id' : $("#salida_id").val(),
      'detalle_unidades' : $("#id_unidades").val(),
      'detalle_costo_unitario' :costo_unitario,
      'entrada2_id' : $("#entrada2_id").val(),
      'salida2_id' : $("#salida2_id").val(),
      'ajustar_primerconteo': $("#id_ajusteprimerconteo").attr('checked')== 'checked',
      'is_mobile': $("#is_mobile").val(),
      }); 
    
    $("#enviar_btn").attr("disabled",true);
    $("#enviar_btn").text("Enviando...");
  }
  else
  {
    if ($('#id_costo_unitario').val() == '')
    { 
      alert("El campo costo unitario es obligatorio");
      $("#id_costo_unitario").focus();
      return;
    }
    else if ($.isNumeric($('#id_costo_unitario').val()) == false )
    {
      alert("Costo unitario incorrecto");
      $("#id_costo_unitario").focus();
      return;
    }
  }
}

function resultado(data)
{
  if ( $("#is_mobile").val() == 'False' )
    window.location = "/inventarios/inventariofisico/"+data.alamcen_id+"/";
  else
  {
    limpiarForm();
    $("#ultimo_conteo").html("<strong>Ultimo conteo</strong><br> "+data.articulo_nombre+"<br>Ex Acual. "+data.existencia_actual+"");
  }
}

/* Mostrar articulo */
function cargar_articulo( articulo_id, articulo_nombre, existencias, costo_ultima_compra, detalle_modificacionestime, ya_ajustado, detalle_modificacionestime_salidas, articulo_seguimiento, articulo_linea )
{
  $('#id_articulo-deck').attr('style','');
  $('#id_articulo-deck').html('<span class="div hilight" data-value="'+articulo_id+'"><span style="display: inline;" class="remove div">X</span>'+articulo_nombre+'</span>');
  $('#id_articulo').html('<option selected="selected" value="'+articulo_id+'"></option>');
  $('#id_articulo_text').hide();
  
  cargar_detallesmovimientos_articulo( detalle_modificacionestime, detalle_modificacionestime_salidas, existencias, ya_ajustado, articulo_seguimiento, articulo_linea );
  
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
/* Mostrar articulo > detalles*/
function cargar_detallesmovimientos_articulo(entradas_detalles, salidas_detalles, existencias, ya_ajustado, seguimiento, articulo_linea )
{
  $("#label_linea").html("<strong>Linea&nbsp;</strong>"+ articulo_linea);
  $(".span_clave").hide();
  $(".span_articulo, #span_nombre_articulo").show();

  $("#articulo_seguimiento").val(seguimiento);
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
  $("#span_nombre_articulo").hide();
  $("#buscar_btn").hide();
  $(".span_unidades, #cancelar_btn").show();
  $('#span_alerta_unidades').html(existencias + " en existencia. <a tabindex='-1' href='#modal_movimientos_articulo' role='button' data-toggle='modal'><i class='icon-info-sign icon-white'></i></a> ");

  var entradas = entradas_detalles.split(',');
  var salidas = salidas_detalles.split(',');
  
  var detalles_html = '<h5> ENTRADAS: </h5>';
  
  $.each(entradas, function(key, entrada) {
    numero = key + 1;
    if (entrada != "")
      detalles_html = detalles_html + numero + ") " + entrada + '<br>';
  });

  detalles_html = detalles_html + '<h5> SALIDAS: </h5>';
  
  $.each(salidas, function(key, salida) {
    numero = key + 1;
    if (salida != "")
      detalles_html = detalles_html + numero + ") " + salida + '<br>';
  });

  $("#modal_movimientos_articulo > .modal-body").html(detalles_html);  
}

/* Buscar articulo */
function mostrar_articulo_byclave(data)
{
  
  if (data.error_msg == "no_existe_clave")
  {
    var opciones = data.opciones_clave;
    var html_var = "<table><tr><th>Clave</th><th>Articulo</td><tr/>";
    var no_opciones = 0;
    for (art in opciones)
    { 
      no_opciones = no_opciones +  1;
      html_var = html_var + "<tr><td><a href='#' class='clave_link'>" + art + "</a></td>" + "<td>" + opciones[art] + "</td></tr>"
    }
    html_var = html_var + "</table>";
    if (no_opciones > 0)
    {
      $("#modal_opciones-claves > .modal-body").html(html_var);
      $(".clave_link").on("click",function(){
        $("#id_claveArticulo").val($(this).text());
        $("#modal_opciones-claves").modal("hide");
        Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(mostrar_articulo_byclave,{
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
    cargar_articulo( data.articulo_id, data.articulo_nombre, data.existencias, data.costo_ultima_compra, data.detalle_modificacionestime, data.ya_ajustado, data.detalle_modificacionestime_salidas, data.articulo_seguimiento, data.articulo_linea );

  }
}

function mostrar_articulo_byid(data) 
{
  cargar_detallesmovimientos_articulo( data.detalle_modificacionestime, data.detalle_modificacionestime_salidas, data.existencias, data.ya_ajustado , data.articulo_seguimiento, data.articulo_linea);
  $("#id_costo_unitario").val(data.costo_ultima_compra);

}

/* Otras funcionalidades */
function load_localstorage()
{
  ajustar_primerconteo = localStorage.getItem("ajustar_primerconteo");
  if (ajustar_primerconteo == false)
    localStorage.setItem("ajustar_primerconteo", 'false');
  

  if( localStorage.getItem("ajustar_primerconteo") === 'true')
    $("#id_ajusteprimerconteo").attr('checked', true);
  else
    $("#id_ajusteprimerconteo").attr('checked', false);

  if( localStorage.getItem("ajustar_primerconteo") === true)
    alert(localStorage.getItem("ajustar_primerconteo"));


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

function buscarClave()
{
  if( $("#id_claveArticulo").val() != '' )
    Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byclave(mostrar_articulo_byclave,{
      'articulo_clave': $("#id_claveArticulo").val(), 
      'almacen': $("#almacen_nombre").val(), 
      'entrada_id' : $("#entrada_id").val(),
    });
  else
    $("#id_articulo_text").focus();
}

$('#id_claveArticulo').live('keydown', function(e) { 
  var keyCode = e.keyCode || e.which; 

  if (keyCode == 13 || keyCode == 9) 
  { 

    buscarClave();
    /*return false*/
  }

});

$("#id_articulo").change(function(){
  if( $("#id_articulo").val() == null )
  {
    $('#span_alerta_unidades, #span_ya_ajustado, #span_sin_ajustado').hide();
     $("#span_nombre_articulo").show();
    $('#id_costo_unitario').val('');
    $("#id_articulo_text").focus();
  }
  else
  {
    Dajaxice.microsip_web.apps.inventarios.get_existenciasarticulo_byid(mostrar_articulo_byid,{
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
{
  $("#chbx_modorapido").attr('checked', true);
  $('#id_ajusteprimerconteo').attr("checked", false);
}


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

$('#id_ajusteprimerconteo').on("click", function(){
  if ($('#id_ajusteprimerconteo').attr('checked') == 'checked')
    localStorage.setItem("ajustar_primerconteo", 'true');
  else
    localStorage.setItem("ajustar_primerconteo", 'false');
});