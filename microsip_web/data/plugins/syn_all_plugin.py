#encoding:utf-8
'''
    Plugin para:
        * Sincronizar algunos datos en todas las empresas
    
    Como Activar:
        1) Indicar la base de datos default
        2) Agragar este archivo a los plugins en la aplicacion
'''
from .syn_all.syn_ciudad import *
from .syn_all.syn_cliente import *
from .syn_all.syn_cliente_direccion import *
from .syn_all.syn_condicion_pago import *
from .syn_all.syn_condicion_pago_plazo import *
from .syn_all.syn_estado import *
from .syn_all.syn_impuesto import *
from .syn_all.syn_pais import *
from .syn_all.syn_estado import *
from .syn_all.syn_articulo import *
from .syn_all.syn_articulo_clave import *
from .syn_all.syn_articulo_impuesto import *
from .syn_all.syn_articulo_linea import *
from .syn_all.syn_articulo_linea_grupo import *