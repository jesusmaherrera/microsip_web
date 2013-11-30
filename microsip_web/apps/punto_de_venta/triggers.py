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
    declare variable linea_puntos integer;
    declare variable linea_pct_dinero_electronico double PRECISION;

    declare variable grupo_puntos integer;
    declare variable grupo_pct_dinero_electronico double PRECISION;

    /*Documento*/
    declare variable documento_total_puntos integer;
    declare variable documento_total_dinero_electronico double PRECISION;

    /*Cliente*/
    declare variable cliente_id integer;
    declare variable cliente_tipo_tarjeta char(1);
    declare variable cliente_total_puntos integer;
    declare variable cliente_total_dinero_electronico double PRECISION;
    declare variable cliente_heredar_puntos_a char(99);

    /*Temporales*/
    declare variable puntos integer;
    declare variable pct_dinero_electronico double PRECISION;
    declare variable dinero_electronico double PRECISION;

    BEGIN
        /*Datos del documento*/
        SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, doctos_pv.sic_puntos, doctos_pv.sic_dinero_electronico, clientes.sic_heredar_puntos_a
        FROM clientes, doctos_pv, doctos_pv_det
        WHERE
            doctos_pv.docto_pv_id =  doctos_pv_det.docto_pv_id and
            doctos_pv.sic_cliente_tarjeta = clientes.cliente_id and
            doctos_pv_det.docto_pv_det_id = new.docto_pv_det_id
        INTO :cliente_id, :cliente_tipo_tarjeta, :cliente_total_puntos, :cliente_total_dinero_electronico, :documento_total_puntos, :documento_total_dinero_electronico, :cliente_heredar_puntos_a;


        if(not cliente_heredar_puntos_a is null)then
        begin
            select clientes.cliente_id
            from clientes, claves_clientes
            where clientes.cliente_id = claves_clientes.cliente_id and claves_clientes.clave_cliente = :cliente_heredar_puntos_a
            into :cliente_id;

            SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, clientes.sic_heredar_puntos_a
            FROM clientes
            WHERE
                clientes.cliente_id = :cliente_id
            INTO :cliente_id, :cliente_tipo_tarjeta, :cliente_total_puntos, :cliente_total_dinero_electronico, :cliente_heredar_puntos_a;
        end

        /*Datos del articulo*/
        SELECT articulos.sic_puntos, articulos.sic_dinero_electronico, lineas_articulos.sic_puntos, lineas_articulos.sic_dinero_electronico,  grupos_lineas.sic_puntos, grupos_lineas.sic_dinero_electronico, articulos.sic_hereda_puntos, lineas_articulos.sic_hereda_puntos
        FROM articulos, lineas_articulos, grupos_lineas
        WHERE
            lineas_articulos.linea_articulo_id = articulos.linea_articulo_id AND
            grupos_lineas.grupo_linea_id = lineas_articulos.grupo_linea_id AND
            articulos.articulo_id = new.articulo_id
        INTO :articulo_puntos, :articulo_pct_dinero_electronico, :linea_puntos, :linea_pct_dinero_electronico, :grupo_puntos, :grupo_pct_dinero_electronico, :articulo_hereda_puntos, :linea_hereda_puntos;

        if (documento_total_puntos is null) then
            documento_total_puntos = 0;
        if (documento_total_dinero_electronico is null) then
            documento_total_dinero_electronico = 0;
        if (cliente_total_puntos is null) then
            cliente_total_puntos = 0;
        if (cliente_total_dinero_electronico is null) then
            cliente_total_dinero_electronico = 0;

        if(cliente_tipo_tarjeta = 'P') then
        begin
            if (articulo_hereda_puntos = 1) then
            begin
                if (linea_hereda_puntos = 1) then
                    puntos = grupo_puntos;
                else
                    puntos = linea_puntos;
            end
            else        
                puntos = articulo_puntos;

            if (puntos is null) then
                puntos = 0;
            new.sic_puntos = (new.unidades * puntos);
        end
        else if(cliente_tipo_tarjeta = 'D') then
        begin
            
            if (articulo_hereda_puntos = 1) then
            begin
                if (linea_hereda_puntos = 1) then
                    pct_dinero_electronico = grupo_pct_dinero_electronico;
                else
                    pct_dinero_electronico = linea_pct_dinero_electronico;
            end
            else        
                pct_dinero_electronico = articulo_pct_dinero_electronico;
            if (pct_dinero_electronico is null) then
                pct_dinero_electronico = 0;

            dinero_electronico = (new.unidades * new.precio_unitario) * (pct_dinero_electronico /100);
            new.sic_dinero_electronico = dinero_electronico ;
        end

        if (new.sic_puntos is null) then
            new.sic_puntos = 0;
        if (new.sic_dinero_electronico is null) then
            new.sic_dinero_electronico = 0;

        documento_total_puntos = documento_total_puntos + new.sic_puntos - old.sic_puntos;
        documento_total_dinero_electronico = documento_total_dinero_electronico + new.sic_dinero_electronico-old.sic_dinero_electronico;

        cliente_total_puntos = cliente_total_puntos + documento_total_puntos - old.sic_puntos;
        cliente_total_dinero_electronico = cliente_total_dinero_electronico + documento_total_dinero_electronico - old.sic_dinero_electronico;

        update doctos_pv set sic_puntos=:documento_total_puntos, sic_dinero_electronico=:documento_total_dinero_electronico where docto_pv_id = new.docto_pv_id;
        update clientes set sic_puntos=:cliente_total_puntos, sic_dinero_electronico=:cliente_total_dinero_electronico where cliente_id = :cliente_id;
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
    declare variable cliente_id integer;
    declare variable cliente_eventual_id integer;
    declare variable tipo_cliente_nombre char(50);
    declare variable cliente_tipo_tarjeta char(1);
    declare variable cliente_total_puntos integer;
    declare variable cliente_total_dinero_electronico double PRECISION;
    declare variable cliente_hereda_valorpuntos smallint;
    declare variable cliente_valor_puntos double PRECISION;
    declare variable tipo_cliente_valor_puntos double PRECISION;
    declare variable valor_puntos double PRECISION;

    /*variables de pagos*/
    declare variable valor_puntos_pago double PRECISION;
    declare variable puntos_pago integer;
    declare variable dinero_electronico_pago double PRECISION;

    begin
        if (new.tipo_docto = 'V') then
        begin
            /*Datos del cliente tarjeta*/
            SELECT tipos_clientes.nombre
            FROM clientes, tipos_clientes
            WHERE clientes.cliente_id = new.cliente_id and clientes.tipo_cliente_id = tipos_clientes.tipo_cliente_id
            INTO :tipo_cliente_nombre;

            /* Para manejo de tarjetas */
            select valor from registry where nombre = 'CLIENTE_EVENTUAL_PV_ID'
            into :cliente_eventual_id;
            if ( new.sic_cliente_tarjeta is null ) then
                new.sic_cliente_tarjeta = 0;
            if ( new.cliente_id <> cliente_eventual_id ) then
                new.sic_cliente_tarjeta = new.cliente_id;
            if (tipo_cliente_nombre = 'TARJETA PROMOCION') then
                new.cliente_id = cliente_eventual_id;

            /*Datos del cliente*/
            SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, clientes.sic_hereda_valorpuntos, clientes.sic_valor_puntos, tipos_clientes.sic_valor_puntos
            FROM clientes, tipos_clientes
            WHERE clientes.cliente_id = new.sic_cliente_tarjeta and clientes.tipo_cliente_id = tipos_clientes.tipo_cliente_id
            INTO :cliente_id, :cliente_tipo_tarjeta, :cliente_total_puntos, :cliente_total_dinero_electronico, :cliente_hereda_valorpuntos, :cliente_valor_puntos, :tipo_cliente_valor_puntos;

            if(tipo_cliente_valor_puntos is null) then
                tipo_cliente_valor_puntos = 0;
            if(cliente_valor_puntos is null) then
                cliente_valor_puntos = 0;
            if (cliente_total_dinero_electronico is null) then
                cliente_total_dinero_electronico = 0;
            if (cliente_total_puntos is null) then
                cliente_total_puntos = 0;

            if (new.estatus='C') then
                begin
                    cliente_total_dinero_electronico =  cliente_total_dinero_electronico - new.sic_dinero_electronico;
                    cliente_total_puntos = cliente_total_puntos - new.sic_puntos;
                    update clientes set sic_puntos=:cliente_total_puntos, sic_dinero_electronico=:cliente_total_dinero_electronico where cliente_id = :cliente_id;
                end
            else
            begin
                if(cliente_tipo_tarjeta <> 'N' ) then
                begin
                    if (cliente_tipo_tarjeta='D') then
                    begin
                        cliente_total_dinero_electronico =  cliente_total_dinero_electronico - new.dscto_importe + old.dscto_importe;
                        valor_puntos_pago =  0;
                        puntos_pago =  0;
                        dinero_electronico_pago = new.dscto_importe;
                    end
                    else if (cliente_tipo_tarjeta='P') then
                    begin
                        if (cliente_hereda_valorpuntos = 1) then
                            valor_puntos = tipo_cliente_valor_puntos;
                        else
                            valor_puntos = cliente_valor_puntos;

                        if (valor_puntos > 0) then
                        begin
                            puntos_pago =  new.dscto_importe/valor_puntos;
                            cliente_total_puntos = cliente_total_puntos - puntos_pago + (old.dscto_importe/valor_puntos);
                        end
                        else
                        begin
                            cliente_total_puntos = cliente_total_puntos;
                            puntos_pago = 0;
                        end

                        valor_puntos_pago =  valor_puntos;
                        dinero_electronico_pago = 0;
                    end

                    new.sic_dinero_electronico_pago = :dinero_electronico_pago;
                    new.sic_valor_puntos_pago = :valor_puntos_pago;
                    new.sic_puntos_pago = :puntos_pago;

                    if (cliente_total_dinero_electronico >= 0 and cliente_total_puntos >=0 and new.dscto_importe <> old.dscto_importe and new.dscto_importe >0) then
                        update clientes set sic_puntos=:cliente_total_puntos, sic_dinero_electronico=:cliente_total_dinero_electronico where cliente_id = :cliente_id;

                    if (cliente_total_dinero_electronico < 0) then
                    begin
                        cliente_total_dinero_electronico = cliente_total_dinero_electronico + new.dscto_importe;
                        exception ex_cliente_sin_saldo 'El cliente no tiene suficientes Dinero Electronico, solo tiene('||cliente_total_dinero_electronico||' en Dinero electronico.) No se agregara el descuento extra.';
                    end

                    if (cliente_total_puntos < 0) then
                    begin
                        cliente_total_puntos = cliente_total_puntos + puntos_pago;
                        exception ex_cliente_sin_saldo 'El cliente no tiene suficientes puntos, solo tiene('||cliente_total_puntos ||' en puntos.) No se agregara el descuento extra.';
                    end
                end
            end
        end
    end
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