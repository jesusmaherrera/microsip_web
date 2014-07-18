triggers = {}


#####################
#                   #
# DETALLE DE VENTAS #
#                   #
#####################

triggers['SIC_PUNTOS_PV_DOCTOSPVDET_BU'] = '''
    CREATE OR ALTER TRIGGER SIC_PUNTOS_PV_DOCTOSPVDET_BU FOR DOCTOS_PV_DET
    ACTIVE BEFORE UPDATE POSITION 0
    as
    /* Datos de articulos */
    declare variable articulo_hereda_puntos smallint;
    declare variable articulo_puntos integer;
    declare variable articulo_pct_dinero_electronico double PRECISION;

    declare variable linea_hereda_puntos smallint;

    /*Documento*/
    declare variable documento_total_puntos integer;
    declare variable documento_total_dinero_electronico double PRECISION;

    /*Temporales*/
    declare variable linea_articulo_id integer;
    declare variable grupo_linea_id integer;

    /*cliente tarjeta */
    declare variable tarjeta_cliente_id integer;
    declare variable tarjeta_tipo char(1);

    BEGIN
        /*------------------------------------
          ---  SE SACA CLIENTE DE TARJETA  ---
          ------------------------------------  */

        select sic_cliente_tarjeta, sic_puntos, sic_dinero_electronico
        from doctos_pv
        where docto_pv_id = new.docto_pv_id
        into :tarjeta_cliente_id, :documento_total_puntos, :documento_total_dinero_electronico;

        if (documento_total_puntos is null) then
            documento_total_puntos = 0;
        if (documento_total_dinero_electronico is null) then
            documento_total_dinero_electronico = 0;

        if (not tarjeta_cliente_id is null) then
        begin
            /* checar si la tarjeta esta activa */
            select sic_tipo_tarjeta
            from clientes
            where cliente_id = :tarjeta_cliente_id
            into :tarjeta_tipo;
    
    
            if (tarjeta_tipo = 'P' or tarjeta_tipo = 'D') then
            begin
    
                /*------------------------------------
                  --- SE SACAN PUNTOS DEL ARTICULO ---
                  ------------------------------------  */
    
                SELECT sic_puntos, sic_dinero_electronico, sic_hereda_puntos, linea_articulo_id
                FROM articulos
                WHERE articulo_id = new.articulo_id
                INTO :articulo_puntos, :articulo_pct_dinero_electronico, :articulo_hereda_puntos, :linea_articulo_id;
    
                if (not linea_articulo_id is null and articulo_hereda_puntos = 1) then
                begin
                    /*Datos de la linea*/
                    SELECT sic_puntos, sic_dinero_electronico, sic_hereda_puntos, grupo_linea_id
                    FROM lineas_articulos
                    WHERE linea_articulo_id = :linea_articulo_id
                    INTO :articulo_puntos, :articulo_pct_dinero_electronico, :linea_hereda_puntos, :grupo_linea_id;
    
                    if (not grupo_linea_id is null and linea_hereda_puntos = 1) then
                    begin
                        /*Datos del grupo*/
                        SELECT sic_puntos, sic_dinero_electronico
                        FROM grupos_lineas
                        WHERE grupo_linea_id = :grupo_linea_id
                        INTO :articulo_puntos, :articulo_pct_dinero_electronico;
                    end
                end
                
                /*si no tienen puntos se ponen el valor por defecto*/
                if( articulo_puntos is null )then
                    select valor from registry where nombre = 'SIC_PUNTOS_ARTICULO_PUNTOS_PREDET' into :articulo_puntos;
                if( articulo_pct_dinero_electronico is null )then
                    select valor from registry where nombre = 'SIC_PUNTOS_ARTICULO_DINERO_ELECT_PREDET' into :articulo_pct_dinero_electronico;
    
                if(tarjeta_tipo = 'P') then
                    new.sic_puntos = (new.unidades * articulo_puntos);
                else if(tarjeta_tipo = 'D') then
                    new.sic_dinero_electronico = (new.unidades * new.precio_unitario) * (articulo_pct_dinero_electronico /100);
                    
                if (new.sic_puntos is null) then
                    new.sic_puntos = 0;
                if (new.sic_dinero_electronico is null) then
                    new.sic_dinero_electronico = 0;
    
    
                documento_total_puntos = documento_total_puntos + new.sic_puntos - old.sic_puntos;
                documento_total_dinero_electronico = documento_total_dinero_electronico + new.sic_dinero_electronico - old.sic_dinero_electronico;
    
                update doctos_pv set sic_puntos=:documento_total_puntos, sic_dinero_electronico=:documento_total_dinero_electronico where docto_pv_id = new.docto_pv_id;
    
            end
        end
    END
    '''

#####################
#                   #
#      VENTAS       #
#                   #
#####################

triggers['SIC_PUNTOS_PV_DOCTOSPV_BU'] = '''
   CREATE OR ALTER TRIGGER SIC_PUNTOS_PV_DOCTOSPV_BU FOR DOCTOS_PV
    ACTIVE BEFORE UPDATE POSITION 0
    AS
    DECLARE VARIABLE cliente_heredar_puntos_a INTEGER;
    DECLARE VARIABLE cliente_tipo_tarjeta CHAR(1);

    DECLARE VARIABLE cliente_eventual_id INTEGER;
    DECLARE VARIABLE cliente_clave_id INTEGER;

    DECLARE VARIABLE corte_dia INTEGER;
    DECLARE VARIABLE corte_mes INTEGER;
    DECLARE VARIABLE corte_anio INTEGER;
    DECLARE VARIABLE corte_fecha date;
    declare variable ene smallint = 31;
    declare variable feb smallint = 28;
    declare variable mar smallint = 31;
    declare variable abr smallint = 30;
    declare variable may smallint = 31;
    declare variable jun smallint = 30;
    declare variable jul smallint = 31;
    declare variable ago smallint = 30;
    declare variable sep smallint = 30;
    declare variable oct smallint = 31;
    declare variable nov smallint = 30;
    declare variable dic smallint = 31;

    DECLARE VARIABLE cliente_tipo_id INTEGER;
    DECLARE VARIABLE cliente_tipo_nombre char(50);

    /* varialbles para manejo de puntos en documentos */
    DECLARE VARIABLE ventas_puntos INTEGER;
    DECLARE VARIABLE ventas_puntos_pago INTEGER;
    DECLARE VARIABLE ventas_dinero_elect DOUBLE PRECISION;
    DECLARE VARIABLE ventas_dinero_elect_pago DOUBLE PRECISION;

    DECLARE VARIABLE devoluciones_puntos INTEGER;
    DECLARE VARIABLE devoluciones_dinero_elect DOUBLE PRECISION;

    DECLARE VARIABLE documentos_total_puntos INTEGER;
    DECLARE VARIABLE documentos_total_dinero_elect DOUBLE PRECISION;

    /* variables para clientes */
    DECLARE VARIABLE cliente_total_dinero_electronico DOUBLE PRECISION;
    DECLARE VARIABLE cliente_hereda_valorpuntos SMALLINT;
    DECLARE VARIABLE cliente_aplicar_descuento_sin_tarjeta SMALLINT;
    DECLARE VARIABLE cliente_valor_puntos DOUBLE PRECISION;
    DECLARE VARIABLE valor_puntos DOUBLE PRECISION;

    /*variables de pagos*/
    DECLARE VARIABLE valor_puntos_pago DOUBLE PRECISION;
    DECLARE VARIABLE puntos_pago INTEGER;
    DECLARE VARIABLE dinero_electronico_pago DOUBLE PRECISION;

    BEGIN
    feb = mod(corte_anio, 4);
    if (feb=0)then
        feb = 29;
    else
        feb = 28;

        IF (NEW.tipo_docto = 'V' or NEW.tipo_docto = 'D' ) THEN
        BEGIN
            select cliente_id from claves_clientes where clave_cliente = new.clave_cliente into :cliente_clave_id;

            /* CLIENTE PUBLICO EN GENERAL */
            SELECT sic_heredar_puntos_a, tipo_cliente_id
            FROM clientes
            WHERE
                cliente_id = :cliente_clave_id
            INTO :cliente_heredar_puntos_a, :cliente_tipo_id;
            cliente_tipo_nombre = null;

            if (not cliente_tipo_id is null) then
                select nombre from tipos_clientes where tipo_cliente_id = :cliente_tipo_id into :cliente_tipo_nombre;

            select valor from registry where nombre = 'CLIENTE_EVENTUAL_PV_ID' into :cliente_eventual_id;

            if (NEW.sic_cliente_tarjeta is null) then
            begin
                /* Si es una tarjeta de puntos */
                if (cliente_tipo_nombre ='TARJETA PROMOCION') then
                begin
                    if (not cliente_eventual_id is null) then
                    begin
                        NEW.sic_cliente_tarjeta = cliente_clave_id;
                        NEW.cliente_id = cliente_eventual_id;
                    end
                end
                /* Si hereda puntos */
                else if (not cliente_heredar_puntos_a is null ) then
                    NEW.sic_cliente_tarjeta = cliente_heredar_puntos_a;
                /* cualquier otro */
                else
                    NEW.sic_cliente_tarjeta = new.cliente_id;
            end

            /*DATOS DEL CLIENTE TARJETA*/
            SELECT sic_tipo_tarjeta, sic_dinero_electronico, sic_hereda_valorpuntos, sic_valor_puntos, tipo_cliente_id, sic_aplicar_dscto
            FROM clientes
            WHERE cliente_id = NEW.sic_cliente_tarjeta
            INTO :cliente_tipo_tarjeta, :cliente_total_dinero_electronico, :cliente_hereda_valorpuntos, :cliente_valor_puntos, :cliente_tipo_id, :cliente_aplicar_descuento_sin_tarjeta;

            IF (cliente_total_dinero_electronico IS NULL) THEN
                cliente_total_dinero_electronico = 0;
            
            /*DATOS el cliente hereda el valor de los puntos*/
            IF ( NOT cliente_tipo_id IS NULL AND cliente_hereda_valorpuntos = 1) THEN
            BEGIN
                SELECT sic_valor_puntos
                FROM tipos_clientes
                WHERE tipo_cliente_id = :cliente_tipo_id
                INTO :cliente_valor_puntos;
            END

            IF(cliente_valor_puntos IS NULL) THEN
                cliente_valor_puntos = 0;

             /*------------------------------------
              ---  MANEJO DE PAGOS CON PUNTOS  ---
              ------------------------------------  */
            /* Entra solo si se maneja tareja de puntos o dinero electronico
            y si se aplica un descuento */
            
            IF(cliente_tipo_tarjeta = 'N' AND NEW.dscto_importe >0 and cliente_aplicar_descuento_sin_tarjeta = 0 ) THEN
                EXCEPTION ex_cliente_sin_saldo 'NO TIENES PERMITIDO APLICAR DESCUENTOS A ESTE CLIENTE';

            IF((cliente_tipo_tarjeta = 'P' OR cliente_tipo_tarjeta = 'D' ) AND NEW.dscto_importe >0 ) THEN
            BEGIN
                IF (cliente_tipo_tarjeta='D') THEN
                BEGIN
                    valor_puntos_pago =  0;
                    puntos_pago =  0;
                    dinero_electronico_pago = NEW.dscto_importe;
                END
                ELSE IF (cliente_tipo_tarjeta='P') THEN
                BEGIN
                    valor_puntos = cliente_valor_puntos;
                    IF (valor_puntos > 0) THEN
                        puntos_pago =  NEW.dscto_importe/valor_puntos;
                    ELSE
                        puntos_pago = 0;

                    valor_puntos_pago =  valor_puntos;
                    dinero_electronico_pago = 0;
                END

                NEW.sic_dinero_electronico_pago = :dinero_electronico_pago;
                NEW.sic_valor_puntos_pago = :valor_puntos_pago;
                NEW.sic_puntos_pago = :puntos_pago;
                
                /*--------------------------------------------
                  ---  CHECA SALDO SUFICIENTE DEL CLIENTE  ---
                  --------------------------------------------  */
                /* Checa si se puede aplicar descuento con puntos
                [Si el cliente tiene saldo]. */


                select sic_fecha_corte from clientes where cliente_id = NEW.sic_cliente_tarjeta into :corte_fecha;
                if (corte_fecha is null) then
                begin
                    select VALOR FROM REGISTRY WHERE NOMBRE = 'SIC_PUNTOS_CORTE_DIA' INTO :corte_dia;
                    select VALOR FROM REGISTRY WHERE NOMBRE = 'SIC_PUNTOS_CORTE_MES' INTO :corte_mes;
                    select VALOR FROM REGISTRY WHERE NOMBRE = 'SIC_PUNTOS_CORTE_ANIO' INTO :corte_anio;
    
                    if (corte_dia is null or corte_dia = 0) then
                        corte_dia = EXTRACT(DAY FROM CURRENT_DATE );
    
                    if ((corte_mes is null or corte_mes = '0') and
                        (corte_anio is null or corte_anio = '0' ) and
                        (corte_dia>EXTRACT(DAY FROM CURRENT_DATE )))then
                        corte_dia = EXTRACT(DAY FROM CURRENT_DATE );
    
                    if (corte_mes is null or corte_mes = '0' ) then
                        corte_mes = EXTRACT(MONTH FROM CURRENT_DATE );
                    if (corte_anio is null or corte_anio = '0') then
                        corte_anio = EXTRACT(YEAR FROM CURRENT_DATE );

                    if (corte_mes= 1 and corte_dia > ene) then
                        corte_dia = ene;
                    if (corte_mes= 2 and corte_dia > feb) then
                        corte_dia = feb;
                    if (corte_mes= 3 and corte_dia > mar) then
                        corte_dia = mar;
                    if (corte_mes= 4 and corte_dia > abr) then
                        corte_dia = abr;
                    if (corte_mes= 5 and corte_dia > may) then
                        corte_dia = may;
                    if (corte_mes= 6 and corte_dia > jun) then
                        corte_dia = jun;
                    if (corte_mes= 7 and corte_dia > jul) then
                        corte_dia = jul;
                    if (corte_mes= 8 and corte_dia > ago) then
                        corte_dia = ago;
                    if (corte_mes= 9 and corte_dia > sep) then
                        corte_dia = sep;
                    if (corte_mes= 10 and corte_dia > oct) then
                        corte_dia = oct;
                    if (corte_mes= 11 and corte_dia > nov) then
                        corte_dia = nov;
                    if (corte_mes= 12 and corte_dia > dic) then
                        corte_dia = dic;

                    corte_fecha = cast(corte_anio||'-'||corte_mes||'-'||corte_dia as date);
                end

                select sum(sic_puntos), sum(sic_puntos_pago), sum(sic_dinero_electronico), sum(sic_dinero_electronico_pago) from doctos_pv
                where fecha >= :corte_fecha and tipo_docto = 'V' and (estatus = 'N' or estatus = 'D' )and sic_cliente_tarjeta = new.sic_cliente_tarjeta and docto_pv_id <> new.docto_pv_id
                into :ventas_puntos,  :ventas_puntos_pago, :ventas_dinero_elect, :ventas_dinero_elect_pago;

                select sum(sic_puntos), sum(sic_dinero_electronico) from doctos_pv
                where fecha >= :corte_fecha and tipo_docto = 'D' and estatus = 'N' and sic_cliente_tarjeta = new.sic_cliente_tarjeta and docto_pv_id <> new.docto_pv_id
                into :devoluciones_puntos, :devoluciones_dinero_elect;


                if (new.sic_puntos is null) then
                    new.sic_puntos = 0;
                if  (new.sic_puntos_pago is null)then
                    new.sic_puntos_pago = 0;
                if (devoluciones_puntos is null) then
                    devoluciones_puntos =0;
                if (ventas_puntos is null) then
                    ventas_puntos = 0;
                if (ventas_puntos_pago is null) then
                    ventas_puntos_pago = 0;
                if (ventas_dinero_elect is null) then
                    ventas_dinero_elect =0;
                if (ventas_dinero_elect_pago is null) then
                    ventas_dinero_elect_pago =0;
                if (devoluciones_dinero_elect is null) then
                    devoluciones_dinero_elect =0;

                documentos_total_puntos = ventas_puntos - ventas_puntos_pago - devoluciones_puntos + new.sic_puntos - new.sic_puntos_pago;
                documentos_total_dinero_elect =  ventas_dinero_elect - ventas_dinero_elect_pago - devoluciones_dinero_elect + new.sic_dinero_electronico - new.sic_dinero_electronico_pago;

                IF (documentos_total_puntos < 0 and cliente_tipo_tarjeta = 'P') THEN
                BEGIN
                    documentos_total_puntos = (documentos_total_puntos + new.sic_puntos_pago)* cliente_valor_puntos;
                    EXCEPTION ex_cliente_sin_saldo 'El cliente no tiene suficientes puntos, solo tiene('||documentos_total_puntos ||' en puntos.) No se agregara el descuento extra.';                    
                END

                IF (documentos_total_dinero_elect < 0 and cliente_tipo_tarjeta = 'D') THEN
                BEGIN
                    documentos_total_dinero_elect = documentos_total_dinero_elect + NEW.dscto_importe;
                    EXCEPTION ex_cliente_sin_saldo 'El cliente no tiene suficientes Dinero Electronico, solo tiene('||documentos_total_dinero_elect||' en Dinero electronico.) No se agregara el descuento extra.';
                END
            END
        END
    END
    '''
