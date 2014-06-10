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

    /*Cliente*/
    declare variable cliente_id integer;

    /*Temporales*/
    declare variable linea_articulo_id integer;
    declare variable grupo_linea_id integer;

    /*cliente tarjeta */
    declare variable tarjeta_cliente_id integer;
    declare variable heredar_puntos_a_cliente_id integer;
    declare variable tarjeta_tipo char(1);

    BEGIN
        /*------------------------------------
          ---  SE SACA CLIENTE DE TARJETA  ---
          ------------------------------------  */
        select sic_cliente_tarjeta, cliente_id, sic_puntos, sic_dinero_electronico
        from doctos_pv
        where docto_pv_id = new.docto_pv_id
        into :tarjeta_cliente_id, :cliente_id, :documento_total_puntos, :documento_total_dinero_electronico;

        if (documento_total_puntos is null) then
            documento_total_puntos = 0;
        if (documento_total_dinero_electronico is null) then
            documento_total_dinero_electronico = 0;

        /* si no se ha indicado ningun cliente de tarjeta sacarlo */
        if (tarjeta_cliente_id is null) then
        begin
            select sic_heredar_puntos_a
            from clientes
            where cliente_id= :cliente_id
            into :heredar_puntos_a_cliente_id;

            if (heredar_puntos_a_cliente_id is null) then
                tarjeta_cliente_id = heredar_puntos_a_cliente_id;
            else
                tarjeta_cliente_id = cliente_id;
        end

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
            
            /*si no tienen puntos se ponen a  0 */
            if( articulo_puntos is null )then
                articulo_puntos = 0;
            if( articulo_puntos is null )then
                articulo_pct_dinero_electronico = 0;

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
    END
    '''

triggers['SIC_PUNTOS_PV_DOCTOSPVDET_AD'] = '''
    CREATE OR ALTER TRIGGER SIC_PUNTOS_PV_DOCTOSPVDET_AD FOR DOCTOS_PV_DET
    ACTIVE AFTER DELETE POSITION 0
    AS
    declare variable cliente_id integer;
    /* PUNTOS */
    declare variable total_puntos integer;
    declare variable dinero_electronico double PRECISION;
    BEGIN
        /*Datos del cliente*/
        SELECT clientes.sic_puntos, clientes.cliente_id, clientes.sic_dinero_electronico
        FROM clientes, doctos_pv
        WHERE
            doctos_pv.docto_pv_id = old.docto_pv_id and
            doctos_pv.sic_cliente_tarjeta = clientes.cliente_id
        INTO total_puntos, cliente_id, dinero_electronico;
        
        IF (dinero_electronico IS NULL) then
                dinero_electronico = 0;

        if (total_puntos is null) then
            total_puntos = 0;

        total_puntos = total_puntos - old.sic_puntos;
        dinero_electronico = dinero_electronico - old.sic_dinero_electronico;

        update clientes set sic_puntos=:total_puntos, sic_dinero_electronico=:dinero_electronico where cliente_id = :cliente_id;
    end
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

    DECLARE VARIABLE cliente_tipo_id INTEGER;
    DECLARE VARIABLE cliente_tipo_nombre char(50);

    DECLARE VARIABLE cliente_total_puntos INTEGER;
    DECLARE VARIABLE cliente_total_dinero_electronico DOUBLE PRECISION;
    DECLARE VARIABLE cliente_hereda_valorpuntos SMALLINT;
    DECLARE VARIABLE cliente_valor_puntos DOUBLE PRECISION;
    DECLARE VARIABLE valor_puntos DOUBLE PRECISION;

    /*variables de pagos*/
    DECLARE VARIABLE valor_puntos_pago DOUBLE PRECISION;
    DECLARE VARIABLE puntos_pago INTEGER;
    DECLARE VARIABLE dinero_electronico_pago DOUBLE PRECISION;

    BEGIN
        IF (NEW.tipo_docto = 'V') THEN
        BEGIN
            /* CLIENTE PUBLICO EN GENERAL */
            SELECT sic_heredar_puntos_a, tipo_cliente_id
            FROM clientes
            WHERE
                cliente_id = NEW.cliente_id
            INTO :cliente_heredar_puntos_a, :cliente_tipo_id;

            IF (cliente_heredar_puntos_a IS NULL) THEN
                NEW.sic_cliente_tarjeta = new.cliente_id;
            else
                NEW.sic_cliente_tarjeta = cliente_heredar_puntos_a;

            /* para cambiar el cliente a publico en general
            si es un cliente tipo tarjeta promocion. */
            if (not cliente_tipo_id is null) then
            begin
                select nombre from tipos_clientes where tipo_cliente_id = :cliente_tipo_id into :cliente_tipo_nombre;

                if (cliente_tipo_nombre ='TARJETA PROMOCION') then
                BEGIN
                   select valor from registry where nombre = 'CLIENTE_EVENTUAL_PV_ID' into :cliente_eventual_id;
                    
                   if (not cliente_eventual_id is null) then
                   begin
                       NEW.sic_cliente_tarjeta = NEW.cliente_id;
                       NEW.cliente_id = cliente_eventual_id;
                   end
                END
            end

            /*DATOS DEL CLIENTE TARJETA*/
            SELECT sic_tipo_tarjeta, sic_puntos, sic_dinero_electronico, sic_hereda_valorpuntos, sic_valor_puntos, tipo_cliente_id
            FROM clientes
            WHERE cliente_id = NEW.sic_cliente_tarjeta
            INTO :cliente_tipo_tarjeta, :cliente_total_puntos, :cliente_total_dinero_electronico, :cliente_hereda_valorpuntos, :cliente_valor_puntos, :cliente_tipo_id;

            IF (cliente_total_dinero_electronico IS NULL) THEN
                cliente_total_dinero_electronico = 0;
            IF (cliente_total_puntos IS NULL) THEN
                cliente_total_puntos = 0;

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

            /* SI SE VA A CANCELAR LA VENTA*/
            IF (NEW.estatus='C') THEN
                BEGIN
                    cliente_total_dinero_electronico =  cliente_total_dinero_electronico - NEW.sic_dinero_electronico;
                    cliente_total_puntos = cliente_total_puntos - NEW.sic_puntos;
                    IF (:cliente_total_puntos < 0 ) THEN
                        cliente_total_puntos = 0;
                    IF (:cliente_total_dinero_electronico < 0) THEN
                        cliente_total_dinero_electronico = 0;
                    UPDATE clientes SET sic_puntos=:cliente_total_puntos, sic_dinero_electronico=:cliente_total_dinero_electronico WHERE cliente_id = NEW.sic_cliente_tarjeta;
                END
            ELSE
            BEGIN
                IF(cliente_tipo_tarjeta = 'P' OR cliente_tipo_tarjeta = 'D' ) THEN
                BEGIN
    
                    /* para manejo de pagos por puntos o dinero electronico */
                    IF (NEW.dscto_importe >0 ) THEN
                    BEGIN
                        IF (cliente_tipo_tarjeta='D') THEN
                        BEGIN
                            cliente_total_dinero_electronico =  cliente_total_dinero_electronico - NEW.dscto_importe + OLD.dscto_importe;
                            valor_puntos_pago =  0;
                            puntos_pago =  0;
                            dinero_electronico_pago = NEW.dscto_importe;
                        END
                        ELSE IF (cliente_tipo_tarjeta='P') THEN
                        BEGIN
                            valor_puntos = cliente_valor_puntos;
                            IF (valor_puntos > 0) THEN
                            BEGIN
                                puntos_pago =  NEW.dscto_importe/valor_puntos;
                                cliente_total_puntos = cliente_total_puntos - puntos_pago + (OLD.dscto_importe/valor_puntos);
                            END
                            ELSE
                            BEGIN
                                cliente_total_puntos = cliente_total_puntos;
                                puntos_pago = 0;
                            END
    
                            valor_puntos_pago =  valor_puntos;
                            dinero_electronico_pago = 0;
                        END
    
                        NEW.sic_dinero_electronico_pago = :dinero_electronico_pago;
                        NEW.sic_valor_puntos_pago = :valor_puntos_pago;
                        NEW.sic_puntos_pago = :puntos_pago;
    
                        IF (cliente_total_dinero_electronico >= 0 AND cliente_total_puntos >=0 AND NEW.dscto_importe <> OLD.dscto_importe AND NEW.dscto_importe >0) THEN
                            UPDATE clientes SET sic_puntos=:cliente_total_puntos, sic_dinero_electronico=:cliente_total_dinero_electronico WHERE cliente_id = NEW.sic_cliente_tarjeta;
    
                        IF (cliente_total_dinero_electronico < 0) THEN
                        BEGIN
                            cliente_total_dinero_electronico = cliente_total_dinero_electronico + NEW.dscto_importe;
                            EXCEPTION ex_cliente_sin_saldo 'El cliente no tiene suficientes Dinero Electronico, solo tiene('||cliente_total_dinero_electronico||' en Dinero electronico.) No se agregara el descuento extra.';
                        END
    
                        IF (cliente_total_puntos < 0) THEN
                        BEGIN
                            cliente_total_puntos = cliente_total_puntos + puntos_pago;
                            EXCEPTION ex_cliente_sin_saldo 'El cliente no tiene suficientes puntos, solo tiene('||cliente_total_puntos ||' en puntos.) No se agregara el descuento extra.';
                        END
                    END
                    IF ((NOT NEW.sic_puntos = OLD.sic_puntos) OR(NOT NEW.sic_dinero_electronico = OLD.sic_dinero_electronico)) THEN
                    BEGIN
                        cliente_total_puntos = cliente_total_puntos + NEW.sic_puntos- OLD.sic_puntos;
                        cliente_total_dinero_electronico = cliente_total_dinero_electronico + NEW.sic_dinero_electronico- OLD.sic_dinero_electronico;
                        UPDATE clientes SET sic_puntos=:cliente_total_puntos , sic_dinero_electronico=:cliente_total_dinero_electronico WHERE cliente_id = NEW.sic_cliente_tarjeta;
                    END
                END
            END
        END
    END
    '''

triggers['SIC_PUNTOS_PV_DOCTOSPV_AD'] = '''
    CREATE OR ALTER TRIGGER SIC_PUNTOS_PV_DOCTOSPV_AD FOR DOCTOS_PV
    ACTIVE AFTER DELETE POSITION 0
    AS
    declare variable cliente_id integer;
    /* PUNTOS */
    declare variable total_puntos integer;
    declare variable dinero_electronico double PRECISION;
    BEGIN
        /*Datos del cliente*/
        SELECT clientes.sic_puntos, clientes.cliente_id, clientes.sic_dinero_electronico
        FROM clientes, doctos_pv
        WHERE
        doctos_pv.docto_pv_id = old.docto_pv_id and
        doctos_pv.sic_cliente_tarjeta = clientes.cliente_id
        INTO total_puntos, cliente_id, dinero_electronico;

        IF (dinero_electronico IS NULL) then
            dinero_electronico = 0;

        if (total_puntos is null) then
            total_puntos = 0;

        total_puntos = total_puntos - old.sic_puntos;
            dinero_electronico = dinero_electronico - old.sic_dinero_electronico;

        update clientes set sic_puntos=:total_puntos, sic_dinero_electronico=:dinero_electronico where cliente_id = :cliente_id;
    end
    '''

#####################
#                   #
#      Clientes     #
#                   #
#####################

triggers['SIC_PUNTOS_PV_CLIENTES_BU'] = '''
    CREATE OR ALTER TRIGGER SIC_PUNTOS_PV_CLIENTES_BU FOR CLIENTES
    ACTIVE BEFORE UPDATE POSITION 0
    AS
    begin
          if (new.sic_puntos <> old.sic_puntos or new.sic_dinero_electronico <> old.sic_dinero_electronico) then
          begin
            if (new.sic_puntos < 0 and new.sic_tipo_tarjeta='P') then
                exception ex_cliente_sin_saldo 'El cliente no tiene suficientes puntos, solo tiene('||old.sic_puntos||' en Puntos.)';
            else if (new.sic_dinero_electronico < 0 and new.sic_tipo_tarjeta='D') then
                exception ex_cliente_sin_saldo 'El cliente no tiene suficientes Dinero Electronico, solo tiene('||old.sic_dinero_electronico||' en Dinero electronico.)';
          end

    end
    '''