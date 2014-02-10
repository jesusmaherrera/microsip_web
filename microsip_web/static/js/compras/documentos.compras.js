function resultado(data){
	location.reload();
}

$("a[class*='aplicar_btn']").on("click", function(){
	event.preventDefault();
	Dajaxice.microsip_web.apps.compras.aplicar_docto( resultado, { 
			'docto_id': $(this).parent().find(".documento_id").val(),
	});  

});

