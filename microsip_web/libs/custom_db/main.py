from django.db import connection

def next_id(generator_name):
    """ return next value of sequence """
    c = connection.cursor()
    c.execute("SELECT GEN_ID(%s , 1 ) FROM RDB$DATABASE;"% generator_name)
    row = c.fetchone()
    return int(row[0])