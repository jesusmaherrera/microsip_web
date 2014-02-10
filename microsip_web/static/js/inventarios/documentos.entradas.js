function resultado(data){
	location.reload();
}

$("a[class*='aplicar_btn']").on("click", function(){
	event.preventDefault();
	Dajaxice.microsip_web.apps.inventarios.aplicar_doctoin( resultado, { 
			'doctoin_id': $(this).parent().find(".entrada_id").val(),
	});  

});



