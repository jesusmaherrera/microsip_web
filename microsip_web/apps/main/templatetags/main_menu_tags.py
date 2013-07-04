from django import template
from  microsip_web.settings.common import MICROSIP_MODULES
register = template.Library()


def microsip_module_btn(ms_module):
   result = ''
   if ms_module in MICROSIP_MODULES:
      if ms_module == 'microsip_web.apps.ventas':
         result = '<li><a href="/ventas/Facturas/"> <i class="msicon-ventas"></i><label class="labelMenu"> Ventas</label></a></li>'
      elif ms_module == 'microsip_web.apps.inventarios':
         result ='<li><a href="/inventarios/Entradas/"> <i class="msicon-inventarios"></i><label class="labelMenu"> Inventarios</label></a></li>'
      elif ms_module == 'microsip_web.apps.cuentas_por_pagar':
         result ='<li><a  href="/cuentas_por_pagar/GenerarPolizas/"> <i class="msicon-cuentas_por_pagar"></i><label class="labelMenu"> Cuentas por pagar</label></a></li>'
      elif ms_module == 'microsip_web.apps.cuentas_por_cobrar':
         result = '<li><a href="/cuentas_por_cobrar/GenerarPolizas/"> <i class="msicon-cuentas_por_cobrar"></i><label class="labelMenu"> Cuentas por cobrar</label></a></li>'
      elif ms_module == 'microsip_web.apps.contabilidad':
         result = '<li><a href="/contabilidad/polizas_pendientes/"> <i class="msicon-contabilidad"></i><label class="labelMenu"> Contabilidad</label></a></li>'
      elif ms_module == 'microsip_web.apps.punto_de_venta':
         result ='<li><a href="/punto_de_venta/ventas/"> <i class="msicon-punto_de_venta"></i><label class="labelMenu"> Punto de venta</label></a></li>'
      elif ms_module == 'microsip_web.apps.compras':
         result = '<li><a href="#"> <i class="msicon-compras"></i><label class="labelMenu"> Compras</label></a></li>'
   
   return result

register.simple_tag(microsip_module_btn)