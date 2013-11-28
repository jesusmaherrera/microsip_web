function get_articulo_byclave(clave, comun_name)
{ 
  if( clave != '' )
    Dajaxice.microsip_web.apps.inventarios.get_articulo_byclave( seleccionar_articulo , { 'clave': clave, 'comun_name': comun_name,} );
}

function seleccionar_articulo(data)
{ 
  /*
    Parametros:
      - data.articulo_id
      - data.articulo_nombre
      - data.comun_name

      - data.opciones_clave
  */
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

    // Dajaxice.microsip_web.apps.inventarios.get_detallesarticulo_byid( cargar_detallesarticulo, { 
    //     'articulo_id': data.articulo_id,
    //     'comun_name': data.comun_name,
    //     'articulo_clave': clave_articulo.val(),
    //   } 
    // );
  }
}