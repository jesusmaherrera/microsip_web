procedures = {}

procedures['SIC_ALERTA_ARTICULO_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_ALERTA_ARTICULO_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_ALERTA_UNIDADES')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_ALERTA_UNIDADES INTEGER DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'SIC_ALERTA_UNIDAD_MEDIDA')) then
            execute statement 'ALTER TABLE ARTICULOS ADD SIC_ALERTA_UNIDAD_MEDIDA VARCHAR(20)';
    END  
    '''