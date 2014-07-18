from django import template
from django.conf import settings

register = template.Library()

def alertas_tab():
  result = ''
  if 'microsip_web.apps.main.comun.articulos.articulos.alertas' in settings.MICROSIP_MODULES:
    result = '<li class=""><a href="#alertas" data-toggle="tab">Alertas</a></li>'
  return result

def articulos_tab():
  result = ''
  if 'microsip_web.apps.main.comun.clientes.clientes.cliente_articulos' in settings.MICROSIP_MODULES:
    result = '<li class=""><a href="#articulos" data-toggle="tab">Articulos</a></li>'
  return result

def generar_polizas_tag(tag_name):
   result = ''
   if 'microsip_web.apps.punto_de_venta.generar_polizas' in settings.MICROSIP_MODULES:
      if tag_name == 'generar_polizas':
         result = '<li><a tabindex="-1" href="/punto_de_venta/GenerarPolizas/"><i class="icon-share"></i> Generar Polizas Contables</a></li>\
        <li role="presentation" class="divider"></li>'
   return result

def informacion_contable_tab():
  result = ''
  if 'microsip_web.apps.punto_de_venta.generar_polizas' in settings.MICROSIP_MODULES:
    result = '<li class=""><a href="#informacion_contable" data-toggle="tab">Informacion contable</a></li>'
  return result

register.simple_tag(articulos_tab)
register.simple_tag(alertas_tab)
register.simple_tag(informacion_contable_tab)

register.simple_tag(generar_polizas_tag)