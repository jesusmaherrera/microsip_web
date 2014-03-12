from django import template
from django.conf import settings

register = template.Library()

def puntos_tab():
  result = ''
  if 'microsip_web.apps.punto_de_venta.puntos' in settings.MICROSIP_MODULES:
    result = '<li class=""><a href="#puntos" data-toggle="tab">Puntos</a></li>'
  return result

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

def puntos_tag(tag_name):
   result = ''
   if 'microsip_web.apps.punto_de_venta.puntos' in settings.MICROSIP_MODULES:
      if tag_name == 'generar_tarjetas':
         result = '<li role="presentation" class="divider"></li><li><a tabindex="-1" href="/punto_de_venta/generar_tarjetas/"><i class="icon-user"></i> Generar Lote de tarjetas</a></li>'
      if tag_name == 'inicializar_puntos':
         result ='<li role="presentation" class="divider"></li><li><a tabindex="-1" href="#myModal_inicializar_puntos_clientes" data-toggle="modal" >\
         <i class="icon-warning-sign" style="margin-left: 0px;"></i> Inicializar puntos de clientes</a></li>\
         <li><a tabindex="-1" href="#myModal_inicializar_puntos_articulos" data-toggle="modal">\
          <i class="icon-warning-sign" style="margin-left: 0px;"></i> Inicializar puntos de Articulos</a></li>'
      if tag_name == 'puntos_form':
        result = '<div class="tab-pane fade " id="puntos">\
          <div>\
            <label>Hereda puntos o dinero electronico</label>\
            <div class="input-prepend input-append">{{ form.hereda_puntos }}</div>\
            </div>\
            <div id="div_puntos">\
              <label>Puntos</label>\
              <div class="input-prepend input-append">{{ form.puntos }}</div>\
            </div>\
            <div id="div_dinero_electronico" >\
              <label>Dinero Elecronico (% de costo)</label>\
              <div class="input-prepend input-append">{{ form.dinero_electronico }}</div>\
            </div>\
          </div>'
      
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

def generar_polizas_tag(tag_name):
   result = ''
   if 'microsip_web.apps.punto_de_venta.generar_polizas' in settings.MICROSIP_MODULES:
      if tag_name == 'informacion_contable_form':
        result = '<div class="tab-pane fade " id="puntos">\
          <div>\
            <label>Hereda puntos o dinero electronico</label>\
            <div class="input-prepend input-append">{{ form.hereda_puntos }}</div>\
            </div>\
            <div id="div_puntos">\
              <label>Puntos</label>\
              <div class="input-prepend input-append">{{ form.puntos }}</div>\
            </div>\
            <div id="div_dinero_electronico" >\
              <label>Dinero Elecronico (% de costo)</label>\
              <div class="input-prepend input-append">{{ form.dinero_electronico }}</div>\
            </div>\
          </div>'
      
   return result
register.simple_tag(articulos_tab)
register.simple_tag(alertas_tab)
register.simple_tag(puntos_tag)
register.simple_tag(puntos_tab)
register.simple_tag(informacion_contable_tab)

register.simple_tag(generar_polizas_tag)