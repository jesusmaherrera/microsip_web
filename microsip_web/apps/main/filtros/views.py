from django.db import connections

def get_next_id_carpeta(connection_name=None):
    """ return next value of sequence """
    c = connections[connection_name].cursor()
    c.execute('SELECT NEXT VALUE FOR "SIC_CARPETA_SQ" FROM RDB$DATABASE;')
    row = c.fetchone()
    return int(row[0])


