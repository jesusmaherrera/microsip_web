from django.db import connections

def next_id(generator_name, connection_name = None):
    """ return next value of sequence """
    c = connections[connection_name].cursor()
    c.execute("SELECT GEN_ID(%s , 1 ) FROM RDB$DATABASE;"% generator_name)
    row = c.fetchone()
    return int(row[0])

def get_conecctionname(session =None):
	basedatos_activa = session['selected_database']
	if basedatos_activa != '':
	    conexion_activa_id = session['conexion_activa']
	    return "%02d-%s"%(conexion_activa_id, basedatos_activa)
	else:
		return ''