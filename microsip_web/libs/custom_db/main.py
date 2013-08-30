from django.db import connections

def next_id(generator_name, connection_name = None):
    """ return next value of sequence """
    c = connections[connection_name].cursor()
    c.execute("SELECT GEN_ID(%s , 1 ) FROM RDB$DATABASE;"% generator_name)
    row = c.fetchone()
    return int(row[0])

def get_conecctionname(userprofile =None):
	basedatos_activa = userprofile.basedatos_activa
	if basedatos_activa != '':
	    conexion_activa_id = userprofile.conexion_activa.id
	    return "%02d-%s"%(conexion_activa_id, basedatos_activa)
	else:
		return ''