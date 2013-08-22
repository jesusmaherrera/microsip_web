from django.db import connections

def next_id(generator_name, database = None):
    """ return next value of sequence """
    c = connections[database].cursor()
    c.execute("SELECT GEN_ID(%s , 1 ) FROM RDB$DATABASE;"% generator_name)
    row = c.fetchone()
    return int(row[0])