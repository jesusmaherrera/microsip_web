from django.db import connection

def get_next_id_carpeta():
    """ return next value of sequence """
    c = connection.cursor()
    c.execute('SELECT NEXT VALUE FOR "SIC_CARPETA_SQ" FROM RDB$DATABASE;')
    row = c.fetchone()
    return int(row[0])


