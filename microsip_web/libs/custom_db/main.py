from django.db import connections
import datetime, time
from microsip_web.libs.api.models import *

def next_id(generator_name, connection_name = None):
    """ return next value of sequence """
    c = connections[connection_name].cursor()
    c.execute("SELECT GEN_ID(%s , 1 ) FROM RDB$DATABASE;"% generator_name)
    row = c.fetchone()
    c.close()
    return int(row[0])

def get_conecctionname(session =None):
	basedatos_activa = session['selected_database']
	if basedatos_activa != '':
	    conexion_activa_id = session['conexion_activa']
	    return "%02d-%s"%(conexion_activa_id, basedatos_activa)
	else:
		return ''

def runsql_firstrow( sql = "", connection_name = "" ):
    c = connections[connection_name].cursor()
    c.execute(sql)
    unidades_rows = c.fetchall()
    c.close() 
    return unidades_rows[0]

def runsql_rows( sql = "", connection_name = "", params=[]):
    c = connections[connection_name].cursor()
    c.execute(sql, params)
    rows = c.fetchall()
    c.close() 
    return rows

def first_or_none(query):  
    try:  
        return query.all()[0]  
    except IndexError:
        return None

def firstALMACENid_or_none(query):  
    try:  
        id = query.all()[0].ALMACEN_ID
        return id
    except IndexError:
        return None

def firstid_or_none(query):  
    try:  
        id = query.all()[0].id
        return id
    except IndexError:
        return None
        
def get_existencias_articulo( articulo_id = None, connection_name = '', fecha_inicio = None, almacen = '' ):
    """ Para obtener las existencias de un articulo determinado """
    fecha_actual_str = datetime.now().strftime("12/31/%Y")
    sql = """
        SELECT B.ENTRADAS_UNID, B.SALIDAS_UNID, B.inv_fin_unid FROM orsp_in_aux_art( %s, '%s', '%s','%s','S','N') B
        """% ( articulo_id , almacen,  fecha_inicio, fecha_actual_str )
    row = runsql_firstrow( sql, connection_name )
    entradas = row[0]
    salidas = row[1]
    inv_fin = row[2]
    
    if not entradas:
        entradas = 0
    if not salidas:
        salidas = 0
    
    existencias = entradas - salidas
    return inv_fin