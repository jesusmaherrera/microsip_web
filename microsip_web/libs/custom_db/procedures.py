procedures = {}

procedures['ventas_inicializar'] = '''
	CREATE OR ALTER PROCEDURE ventas_inicializar
    as
    begin
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_FAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_1')) then
            execute statement 'ALTER TABLE LIBRES_FAC_VE ADD SEGMENTO_1 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_FAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_2')) then
            execute statement 'ALTER TABLE LIBRES_FAC_VE ADD SEGMENTO_2 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_FAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_3')) then
            execute statement 'ALTER TABLE LIBRES_FAC_VE ADD SEGMENTO_3 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_FAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_4')) then
            execute statement 'ALTER TABLE LIBRES_FAC_VE ADD SEGMENTO_4 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_FAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_5')) then
            execute statement 'ALTER TABLE LIBRES_FAC_VE ADD SEGMENTO_5 VARCHAR(99)';

        /*Libres CREDITOS */

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_DEVFAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_1')) then
            execute statement 'ALTER TABLE LIBRES_DEVFAC_VE ADD SEGMENTO_1 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_DEVFAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_2')) then
            execute statement 'ALTER TABLE LIBRES_DEVFAC_VE ADD SEGMENTO_2 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_DEVFAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_3')) then
            execute statement 'ALTER TABLE LIBRES_DEVFAC_VE ADD SEGMENTO_3 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_DEVFAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_4')) then
            execute statement 'ALTER TABLE LIBRES_DEVFAC_VE ADD SEGMENTO_4 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_DEVFAC_VE' and rf.RDB$FIELD_NAME = 'SEGMENTO_5')) then
            execute statement 'ALTER TABLE LIBRES_DEVFAC_VE ADD SEGMENTO_5 VARCHAR(99)';
    end
	'''

procedures['punto_de_venta_inicializar_t'] = '''
	CREATE OR ALTER PROCEDURE punto_de_venta_inicializar_t
    as
    BEGIN
        /*Articulos */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE ARTICULOS ADD PUNTOS SMALLINT DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE ARTICULOS ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ARTICULOS' and rf.RDB$FIELD_NAME = 'HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE ARTICULOS ADD HEREDA_PUNTOS SMALLINT';

        /*Lineas */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD PUNTOS ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LINEAS_ARTICULOS' and rf.RDB$FIELD_NAME = 'HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE LINEAS_ARTICULOS ADD HEREDA_PUNTOS SMALLINT';

        /*Grupos */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD PUNTOS ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'GRUPOS_LINEAS' and rf.RDB$FIELD_NAME = 'HEREDA_PUNTOS')) then
            execute statement 'ALTER TABLE GRUPOS_LINEAS ADD HEREDA_PUNTOS SMALLINT';
            
        /*Clientes */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE CLIENTES ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE CLIENTES ADD PUNTOS ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'TIPO_TARJETA')) then
            execute statement 'ALTER TABLE CLIENTES ADD TIPO_TARJETA CHAR(1)';
        
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'HEREDA_VALORPUNTOS')) then
            execute statement 'ALTER TABLE CLIENTES ADD HEREDA_VALORPUNTOS SMALLINT DEFAULT 1';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'VALOR_PUNTOS')) then
            execute statement 'ALTER TABLE CLIENTES ADD VALOR_PUNTOS IMPORTE_MONETARIO DEFAULT 0';
        
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'HEREDAR_PUNTOS_A')) then
            execute statement 'ALTER TABLE CLIENTES ADD HEREDAR_PUNTOS_A ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_1')) then
            execute statement 'ALTER TABLE CLIENTES ADD CUENTA_1 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_2')) then
            execute statement 'ALTER TABLE CLIENTES ADD CUENTA_2 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_3')) then
            execute statement 'ALTER TABLE CLIENTES ADD CUENTA_3 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_4')) then
            execute statement 'ALTER TABLE CLIENTES ADD CUENTA_4 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_5')) then
            execute statement 'ALTER TABLE CLIENTES ADD CUENTA_5 ENTERO_ID';

        /* libres clientes */

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_1')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD CUENTA_1 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_2')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD CUENTA_2 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_3')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD CUENTA_3 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_4')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD CUENTA_4 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'CUENTA_5')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD CUENTA_5 ENTERO_ID';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CLIENTES' and rf.RDB$FIELD_NAME = 'HEREDAR_PUNTOS_A')) then
            execute statement 'ALTER TABLE LIBRES_CLIENTES ADD HEREDAR_PUNTOS_A ENTERO_ID';

        /*Tipo Cliente */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'TIPOS_CLIENTES' and rf.RDB$FIELD_NAME = 'VALOR_PUNTOS')) then
            execute statement 'ALTER TABLE TIPOS_CLIENTES ADD VALOR_PUNTOS IMPORTE_MONETARIO DEFAULT 0';

        /*Doctos pv det */
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV_DET' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE DOCTOS_PV_DET ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV_DET' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE DOCTOS_PV_DET ADD PUNTOS ENTERO DEFAULT 0';
        /*Doctos pv*/
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD DINERO_ELECTRONICO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'PUNTOS')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD PUNTOS ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'VALOR_PUNTOS_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD VALOR_PUNTOS_PAGO IMPORTE_MONETARIO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'PUNTOS_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD PUNTOS_PAGO ENTERO DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_PV' and rf.RDB$FIELD_NAME = 'DINERO_ELECTRONICO_PAGO')) then
            execute statement 'ALTER TABLE DOCTOS_PV ADD DINERO_ELECTRONICO_PAGO IMPORTE_MONETARIO DEFAULT 0';
    END
    '''
procedures['cuentas_por_pagar_inicializar'] = '''
	CREATE OR ALTER PROCEDURE cuentas_por_pagar_inicializar
    as
    BEGIN
        /*Libres cargos */

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CP' and rf.RDB$FIELD_NAME = 'SEGMENTO_1')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CP ADD SEGMENTO_1 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CP' and rf.RDB$FIELD_NAME = 'SEGMENTO_2')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CP ADD SEGMENTO_2 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CP' and rf.RDB$FIELD_NAME = 'SEGMENTO_3')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CP ADD SEGMENTO_3 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CP' and rf.RDB$FIELD_NAME = 'SEGMENTO_4')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CP ADD SEGMENTO_4 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CP' and rf.RDB$FIELD_NAME = 'SEGMENTO_5')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CP ADD SEGMENTO_5 VARCHAR(99)';
    END
    '''

procedures['cuentas_por_cobrar_inicializar'] = '''
	CREATE OR ALTER PROCEDURE cuentas_por_cobrar_inicializar
    as
    BEGIN
        /*Libres cargos */

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_1')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CC ADD SEGMENTO_1 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_2')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CC ADD SEGMENTO_2 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_3')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CC ADD SEGMENTO_3 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_4')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CC ADD SEGMENTO_4 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CARGOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_5')) then
            execute statement 'ALTER TABLE LIBRES_CARGOS_CC ADD SEGMENTO_5 VARCHAR(99)';


        /*Libres CREDITOS */

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CREDITOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_1')) then
            execute statement 'ALTER TABLE LIBRES_CREDITOS_CC ADD SEGMENTO_1 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CREDITOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_2')) then
            execute statement 'ALTER TABLE LIBRES_CREDITOS_CC ADD SEGMENTO_2 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CREDITOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_3')) then
            execute statement 'ALTER TABLE LIBRES_CREDITOS_CC ADD SEGMENTO_3 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CREDITOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_4')) then
            execute statement 'ALTER TABLE LIBRES_CREDITOS_CC ADD SEGMENTO_4 VARCHAR(99)';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'LIBRES_CREDITOS_CC' and rf.RDB$FIELD_NAME = 'SEGMENTO_5')) then
            execute statement 'ALTER TABLE LIBRES_CREDITOS_CC ADD SEGMENTO_5 VARCHAR(99)';
    END
    '''