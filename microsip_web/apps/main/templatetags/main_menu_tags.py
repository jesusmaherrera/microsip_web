from django import template
from django.conf import settings

register = template.Library()

def microsip_module_btn(ms_module):
   result = ''
   if ms_module == 'admin':
      result = '<li><a href="/"> <i class="msicon-admin"></i></a></li>'

   if ms_module in settings.MICROSIP_MODULES:
      if ms_module == 'microsip_web.apps.ventas':
         result = '<li><a href="/ventas/Facturas/"> <i class="msicon-ventas"></i><label class="small_screen"> Ventas </label></a></li>'
      elif ms_module == 'microsip_web.apps.inventarios':
         result ='<li><a href="/inventarios/inventariosfisicos/"> <i class="msicon-inventarios"></i> <label class="small_screen"> Inventarios</label></a></li>'
      elif ms_module == 'microsip_web.apps.cuentas_por_pagar':
         result ='<li><a  href="/cuentas_por_pagar/GenerarPolizas/"> <i class="msicon-cuentas_por_pagar"></i><label class="small_screen"> Cuentas por pagar</label></a></li>'
      elif ms_module == 'microsip_web.apps.cuentas_por_cobrar':
         result = '<li><a href="/cuentas_por_cobrar/GenerarPolizas/"> <i class="msicon-cuentas_por_cobrar"></i><label class="small_screen"> Cuentas por cobrar </label></a></li>'
      elif ms_module == 'microsip_web.apps.contabilidad':
         result = '<li><a href="/contabilidad/polizas_pendientes/"> <i class="msicon-contabilidad"></i><label class="small_screen"> Contabilidad </label></a></li>'
      elif ms_module == 'microsip_web.apps.punto_de_venta':
         result ='<li><a href="/punto_de_venta/ventas/"> <i class="msicon-punto_de_venta"></i><label class="small_screen"> Punto de venta</label></a></li>'
      elif ms_module == 'microsip_web.apps.compras':
         result = '<li><a href="#"> <i class="msicon-compras"></i><label class="small_screen"> Compras</label></a></li>'
   
   return result

register.simple_tag(microsip_module_btn)