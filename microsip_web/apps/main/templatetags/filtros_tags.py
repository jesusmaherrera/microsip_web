from django import template
from django.conf import settings

register = template.Library()

def agregar_compatibilidad_btn():
   result = ''
   if 'microsip_web.apps.main.filtros' in settings.MICROSIP_MODULES:
      result = '<a href="#" role="button" class="btn dropdown-toggle" data-toggle="dropdown"> <i class="icon-plus-sign"></i> Compatibilidad <b class="caret"></b></a>'
   else:
      result = '<a href="#" role="button" class="btn dropdown-toggle hide" data-toggle="dropdown"> <i class="icon-plus-sign"></i> Compatibilidad <b class="caret"></b></a>'

   return result

def filtros_tab():
   result = ''
   if 'microsip_web.apps.main.filtros' in settings.MICROSIP_MODULES:
      result = '<li class=""><a href="#filtros" data-toggle="tab">Filtros</a></li>'

   return result
def compatibilidad_title():
   result = ''
   if 'microsip_web.apps.main.filtros' in settings.MICROSIP_MODULES:
      result = '<legend>Compatibilidades '
   else:
      result = '<legend>'

   return result

register.simple_tag(agregar_compatibilidad_btn)
register.simple_tag(compatibilidad_title)
register.simple_tag(filtros_tab)