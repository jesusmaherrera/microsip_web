$(document).ready(function() {

    $( "#id_inicio" ).datepicker({dateFormat:'dd/mm/yy',});
    $( "#id_fin" ).datepicker({dateFormat:'dd/mm/yy',});
	$("input[type='checkbox']").on("click", mostrar_botones);
	
	function mostrar_botones(){
		if ($( "input:checked" ).length > 0)
			$("#generar_cargos").removeClass('hidden');
		else
			$("#generar_cargos").addClass('hidden');
	}

	$("#generar_cargos").on("click", generar_cargos);

	function generar_cargos(){
		var ids = '';
		$("input[type='checkbox']").each(function(){
			if (this.checked){
				ids += this.value+ ","
			}
		});
		
		$.ajax({
			data: {'ids':ids},
			url:'/ventas/remisiones_cxc/generar_cargos/',
			type : 'get',
			success: function(data){
				// $("#myModal").modal('hide');
				for (var i = 0; i<data.remisiones_cargadas.length ; i++){
					$("input[type='checkbox'][value='"+data.remisiones_cargadas[i]+"'").parent().parent().children('td').addClass("bg-danger");
					$("input[type='checkbox'][value='"+data.remisiones_cargadas[i]+"'").hide();
				}
				
				keys = Object.keys(data.errors);
				var error_msg = ':( Ocurrio un problema\n\n';
				if (keys.length > 0){
					for (var i = 0; i<keys.length ; i++){
						error_msg += keys[i] + ': '+ data.errors[keys[i]]+'\n';
					}
					alert(error_msg);
				}
				else{
					alert(':) Transacion exitosa');
				}
				
			},


		});
		

	}
});