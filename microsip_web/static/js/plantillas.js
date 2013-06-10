function ajustarFormulario(selecion) {
  if($(selecion).val() == "Segmento_1" || $(selecion).val() == "Segmento_2" || $(selecion).val() == "Segmento_3" || $(selecion).val() == "Segmento_4" || $(selecion).val() == "Segmento_5")
  {    
    $(selecion).parent().parent().find("input[name*='asiento_ingora']").show();
    $(selecion).parent().parent().find("select[name*='valor_iva']").hide();
    $(selecion).parent().parent().find("select[name*='valor_contado_credito']").hide();
  } 
  else if ($(selecion).val() == "IVA")
  {
    $(selecion).parent().parent().find("select[name*='valor_contado_credito']").show();
    $(selecion).parent().parent().find("select[name*='valor_iva']").hide();
    $(selecion).parent().parent().find("input[name*='asiento_ingora']").show();
  }
  else if($(selecion).val() == "Descuentos" || $(selecion).val() == "IVA Retenido" || $(selecion).val() == "Bancos" || $(selecion).val() == "Proveedores" || $(selecion).val() == "Clientes")  
  {
    $(selecion).parent().parent().find("select[name*='valor_contado_credito']").hide();
    $(selecion).parent().parent().find("select[name*='valor_iva']").hide();
    $(selecion).parent().parent().find("input[name*='asiento_ingora']").show();
  }
  else if($(selecion).val() == "Compras" || $(selecion).val() == "Ventas" || $(selecion).val()=='Anticipos')  
  {
    $(selecion).parent().parent().find("select[name*='valor_contado_credito']").show();
    $(selecion).parent().parent().find("select[name*='valor_iva']").show();
    $(selecion).parent().parent().find("input[name*='asiento_ingora']").show(); 
  }
  else if($(selecion).val() == "" )
  {
    $(selecion).parent().parent().find("select[name*='valor_contado_credito']").hide();
    $(selecion).parent().parent().find("select[name*='valor_iva']").hide();
    $(selecion).parent().parent().find("input[name*='asiento_ingora']").hide(); 
  }
}
