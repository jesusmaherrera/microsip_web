from django import template
from django.conf import settings

register = template.Library()

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
      
   return result


def generar_polizas_tag(tag_name):
   result = ''
   if 'microsip_web.apps.punto_de_venta.generar_polizas' in settings.MICROSIP_MODULES:
      if tag_name == 'generar_polizas':
         result = '<li><a tabindex="-1" href="/punto_de_venta/GenerarPolizas/"><i class="icon-share"></i> Generar Polizas Contables</a></li>\
        <li role="presentation" class="divider"></li><li><a tabindex="-1" href="/punto_de_venta/PreferenciasEmpresa/">\
        <i class="icon-cog"></i> Preferencias de la empresa</a></li>'
   return result

register.simple_tag(puntos_tag)
register.simple_tag(generar_polizas_tag)