def split_seq(seq, n):
    """ para separar una lista en otra lista de listas en partes iguales.
    """
    lista = []
    for i in xrange(0, len(seq), n):
        lista.append(seq[i:i+n])
    return lista