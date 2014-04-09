procedures = {}

procedures['SIC_VENTASDOCUMENTO_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_VENTASDOCUMENTO_AT
    as
    BEGIN
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_VE' and rf.RDB$FIELD_NAME = 'SIC_CARGO_GENERADO')) then
            execute statement 'ALTER TABLE DOCTOS_VE ADD SIC_CARGO_GENERADO SMALLINT';
    END  
    '''