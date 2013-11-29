;(function( $ ) {
  $.fn.InputClaveArticulo = function(options) {
    var $inputclave = ''
	  var settings = $.extend({
        // These are the defaults.
        searchFunction: '',
        clavecommun_name: 'clave_articulo',
	  }, options );

    this.initialize = function(){
      return this;
    };

    this.seleccionar_articulo = function( data ) { 
      /*Funcion para selecionar un articulo 
      Parametros: - data.articulo_id - data.articulo_nombre - data.comun_name - data.opciones_clave */
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
          $("#claves_options_container").html(html_var);
          $(".clave_link").on("click",function(){
            $inputclave.val($(this).text())
            $("#modal_opciones-claves").modal("hide");
            var clave = $(this).text();
            var comun_name = data.comun_name;
            settings.searchFunction( seleccionar_articulo , { 'clave': clave, 'comun_name': comun_name,} );
          });
          $("#modal_opciones-claves").modal();
        }
        else
          alert('No existe ningun articulo con la clave ['+ clave_articulo.val() +']');
      }
    }

    var modal_claves ='<div id="modal_opciones-claves" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h3 id="myModalLabel">Claves</h3></div><div class="modal-body" id="claves_options_container"></div></div>'
    $('body').append(modal_claves);

    return this.each(function() {
    	$(this).live('keydown', function(e) { 
    		var keyCode = e.keyCode || e.which; 
    		var clave = $(this).val();
    		var comun_name = $(this).attr('name').replace(settings.clavecommun_name, "");

    		if (keyCode == 13 || keyCode == 9) 
    		{
          $inputclave = $(this);
    			if( clave != '' )    
    		  	settings.searchFunction( seleccionar_articulo , { 'clave': clave, 'comun_name': comun_name,} );
    		  
    		  	if (keyCode == 13 )
    		  		e.preventDefault();
    		}
    	});
  	});

  };
}( jQuery ));