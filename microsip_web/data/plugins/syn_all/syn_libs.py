#encoding:utf-8
''' Libreria de funciones para sincronizar bases de datos. '''

from ....libs.api.models import Registry

default_db = '01-ISAAC_WIEBE_LOEWEN'

def get_indices(bases_de_datos_count, incremento, tipo):
    ''' Obtiene los indices de las bases de datos a sincronizar.'''

    registro = Registry.objects.get( nombre = 'SIC_INDICE_BASES_DATOS_SYN' ).valor
    registro_split = registro.split(';')
    
    if len(registro_split) == 2:
        registro_tipo = registro_split[0]
        indice = int(registro_split[1])
        if registro_tipo != tipo:
            indice = 0
    else:
        indice = 0

    indice_final = indice + incremento
    if indice_final > bases_de_datos_count:
        indice_final = bases_de_datos_count

    return indice, indice_final

def set_indices(indice_final, bases_de_datos_count, tipo):
    ''' Guarda el indice  en el que continuara sincronizando con bases de datos.'''
    
    indice = indice_final
    if indice == bases_de_datos_count:
        indice = 0
    registro = Registry.objects.get( nombre = 'SIC_INDICE_BASES_DATOS_SYN' )
    registro.valor = "%s;%s"%(tipo, indice)
    
    if indice == 0:
        print "La sincronizacion de %sS termino correctamente"%tipo
    else:
        print "Indice en:%s"%indice

    registro.save()