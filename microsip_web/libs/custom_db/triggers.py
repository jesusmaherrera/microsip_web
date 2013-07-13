triggers = {}

#############################
#                           #
#   DESGLOSE EN DISCRETOS   #
#                           #
#############################
triggers['SIC_PUERTA_VE_DESGLOSEDIS_AI'] = '''
    CREATE OR ALTER TRIGGER SIC_PUERTA_VE_DESGLOSEDIS_AI FOR DESGLOSE_EN_DISCRETOS_VE
    ACTIVE AFTER INSERT POSITION 0
    AS
    begin
        delete from desglose_en_discretos_invfis where art_discreto_id = new.art_discreto_id;
    end
    '''

triggers['SIC_PUERTA_PV_DESGLOSEDIS_AI'] = '''
    CREATE OR ALTER TRIGGER SIC_PUERTA_PV_DESGLOSEDIS_AI FOR DESGLOSE_EN_DISCRETOS_PV
    ACTIVE AFTER INSERT POSITION 0
    AS
    begin
        delete from desglose_en_discretos_invfis where art_discreto_id = new.art_discreto_id;
    end
    '''
    
triggers['SIC_PUERTA_C_DESGLOSEDIS_AI'] = '''
    CREATE OR ALTER TRIGGER SIC_PUERTA_C_DESGLOSEDIS_AI FOR DESGLOSE_EN_DISCRETOS_CM
    ACTIVE AFTER INSERT POSITION 0
    AS
    declare variable articulo_id integer;
    declare variable docto_invfis_det_id integer;
    declare variable articulo_discreto_fecha date;
    begin
        select articulo_id
        from articulos_discretos
        where art_discreto_id = new.art_discreto_id
        into :articulo_id;

        select docto_invfis_det_id
        from doctos_invfis_det
        where articulo_id = :articulo_id
        into :docto_invfis_det_id;

        insert into desglose_en_discretos_invfis values(-1, :docto_invfis_det_id, new.art_discreto_id, new.unidades);
    end
    '''

#####################
#                   #
#   DOCTOS_IN_DET   #
#                   #
#####################

triggers['SIC_PUERTA_INV_DOCTOSINDET_BI'] = '''	
	CREATE OR ALTER TRIGGER SIC_PUERTA_INV_DOCTOSINDET_BI FOR DOCTOS_IN_DET
    ACTIVE BEFORE INSERT POSITION 0
    AS
    declare variable invfis_id integer;
    declare variable invfis_det_id integer;
    declare variable articulo_id integer;
    declare variable cantidad_articulos integer;
    declare variable almacen_id integer;
    declare variable existe integer;
    declare variable docto_in_tipo char(1);

    begin

        /*Datos de documento in*/
        select first 1 doctos_in.naturaleza_concepto, doctos_in.almacen_id
        from doctos_in
        where doctos_in.docto_in_id = new.docto_in_id
        INTO :docto_in_tipo, :almacen_id;

        /*Datos de inventario fisico abierto*/
        select first 1 doctos_invfis.docto_invfis_id from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= :almacen_id
        INTO :invfis_id;
    
        if (not invfis_id is null) then
        begin
            existe = 0;
            for
                select doctos_invfis_det.docto_invfis_det_id, doctos_invfis_det.articulo_id, doctos_invfis_det.unidades
                from doctos_invfis, doctos_invfis_det
                where doctos_invfis.docto_invfis_id = doctos_invfis_det.docto_invfis_id and doctos_invfis.docto_invfis_id = :invfis_id
                into :invfis_det_id, :articulo_id, :cantidad_articulos
            do
            begin
                if (new.unidades is null) then
                    new.unidades = 0;
                if (cantidad_articulos is null) then
                    cantidad_articulos = 0;

                if (articulo_id = new.articulo_id) then
                begin
                    existe = 1;
                    if (docto_in_tipo='E') then
                        cantidad_articulos = cantidad_articulos + new.unidades;
                    else if (docto_in_tipo='S') then
                        cantidad_articulos = cantidad_articulos - new.unidades;
                    if (cantidad_articulos < 0 ) then
                        cantidad_articulos = 0;
                    update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;
                end
            end
            if (existe = 0) then
            begin
                if (docto_in_tipo='E') then
                    insert into doctos_invfis_det (docto_invfis_det_id, docto_invfis_id, clave_articulo, articulo_id, unidades) values(-1, :invfis_id, new.clave_articulo, new.articulo_id, new.unidades);
            end
        end
    end
	'''

triggers['SIC_PUERTA_INV_DOCTOSINDET_BD'] = '''
	CREATE OR ALTER TRIGGER SIC_PUERTA_INV_DOCTOSINDET_BD FOR DOCTOS_IN_DET
    ACTIVE BEFORE DELETE POSITION 0
    AS
    declare variable invfis_id integer;
    declare variable invfis_det_id integer;
    declare variable articulo_id integer;
    declare variable cantidad_articulos integer;
    declare variable docto_in_tipo char(1);

    begin
        /*Datos de documento in*/
        select first 1 doctos_in.naturaleza_concepto
        from doctos_in
        where doctos_in.docto_in_id = old.docto_in_id
        INTO :docto_in_tipo;
    
        /*Datos de inventario fisico abierto*/
        select first 1 doctos_invfis.docto_invfis_id from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= old.almacen_id
        INTO :invfis_id;

        if (not invfis_id is null) then
        begin

            for
                select doctos_invfis_det.docto_invfis_det_id, doctos_invfis_det.articulo_id, doctos_invfis_det.unidades
                from doctos_invfis_det
                where doctos_invfis_det.docto_invfis_id =  :invfis_id
                into :invfis_det_id, :articulo_id, :cantidad_articulos
            do
            begin

                if (articulo_id = old.articulo_id and docto_in_tipo='E') then
                    cantidad_articulos = cantidad_articulos - old.unidades;
                else if (articulo_id = old.articulo_id and docto_in_tipo='S') then
                    cantidad_articulos = cantidad_articulos + old.unidades;

                if (cantidad_articulos <0 ) then
                    cantidad_articulos = 0;

                update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;

            end
        end
    end
	'''

#####################
#                   #
#     DOCTOS_IN     #
#                   #
#####################

triggers['SIC_PUERTA_INV_DOCTOSIN_BU'] = '''
	CREATE OR ALTER TRIGGER SIC_PUERTA_INV_DOCTOSIN_BU FOR DOCTOS_IN
    ACTIVE BEFORE UPDATE POSITION 0
    AS
    declare variable invfis_id integer;

    declare variable invfis_det_id integer;
    declare variable invfis_articulo_id integer;
    declare variable invfis_articulo_unidades integer;

    declare variable inv_articulo_id integer;
    declare variable inv_articulo_unidades integer;

    declare variable almacen_id integer;
    declare variable inv_tipo char(1);

    begin
        if (new.cancelado='S') then
        begin
            /*Datos de documento in*/
            select first 1 doctos_in.naturaleza_concepto, doctos_in.almacen_id
            from doctos_in
            where doctos_in.docto_in_id = new.docto_in_id
            INTO :inv_tipo, :almacen_id;
        
            /*Datos de inventario fisico abierto*/
            select first 1 doctos_invfis.docto_invfis_id from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= :almacen_id
            INTO :invfis_id;
        
            if (not invfis_id is null) then
            begin
                for select doctos_in_det.articulo_id, doctos_in_det.unidades
                from doctos_in,  doctos_in_det
                where doctos_in.docto_in_id = doctos_in_det.docto_in_id
                into :inv_articulo_id, :inv_articulo_unidades
                do
                begin
                    for select doctos_invfis_det.docto_invfis_det_id, doctos_invfis_det.articulo_id, doctos_invfis_det.unidades
                    from doctos_invfis, doctos_invfis_det
                    where doctos_invfis.docto_invfis_id = doctos_invfis_det.docto_invfis_id and doctos_invfis.docto_invfis_id = :invfis_id
                    into :invfis_det_id, :invfis_articulo_id, :invfis_articulo_unidades
                    do
                    begin
                        if (invfis_articulo_id = inv_articulo_id) then
                        begin
                            if(inv_tipo='E') then
                                invfis_articulo_unidades = invfis_articulo_unidades - inv_articulo_unidades;
                            else if (inv_tipo='S') then
                                invfis_articulo_unidades = invfis_articulo_unidades + inv_articulo_unidades;
                            update doctos_invfis_det set unidades= :invfis_articulo_unidades where docto_invfis_det_id = :invfis_det_id;
                        end
                    end            
                end
            end
        end
    end
	'''

#####################
#                   #
# DETALLE DE VENTAS #
#                   #
#####################

triggers['DOCTOS_PV_DET_BU_PUNTOS'] = '''
	CREATE OR ALTER TRIGGER DOCTOS_PV_DET_BU_PUNTOS FOR DOCTOS_PV_DET
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
        SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, doctos_pv.sic_puntos, doctos_pv.sic_dinero_electronico, libres_clientes.heredar_puntos_a
        FROM clientes, doctos_pv, doctos_pv_det, libres_clientes
        WHERE
            doctos_pv.docto_pv_id =  doctos_pv_det.docto_pv_id and
            doctos_pv.cliente_id = clientes.cliente_id and
            doctos_pv_det.docto_pv_det_id = new.docto_pv_det_id and
            clientes.cliente_id = libres_clientes.cliente_id
        INTO :cliente_id, :cliente_tipo_tarjeta, :cliente_total_puntos, :cliente_total_dinero_electronico, :documento_total_puntos, :documento_total_dinero_electronico, :cliente_heredar_puntos_a;


        if(not cliente_heredar_puntos_a is null)then
        begin
            select clientes.cliente_id
            from clientes, claves_clientes
            where clientes.cliente_id = claves_clientes.cliente_id and claves_clientes.clave_cliente = :cliente_heredar_puntos_a
            into :cliente_id;

            SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, libres_clientes.heredar_puntos_a
            FROM clientes, libres_clientes
            WHERE
                clientes.cliente_id = libres_clientes.cliente_id and
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

triggers['DOCTOS_PV_DET_AD_PUNTOS'] = '''
	CREATE OR ALTER TRIGGER DOCTOS_PV_DET_AD_PUNTOS FOR DOCTOS_PV_DET
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
            doctos_pv.cliente_id = clientes.cliente_id
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

triggers['DOCTOS_PV_BU_PUNTOS'] = '''
	CREATE OR ALTER TRIGGER DOCTOS_PV_BU_PUNTOS FOR DOCTOS_PV
    ACTIVE BEFORE UPDATE POSITION 0
    AS
    declare variable cliente_id integer;
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
        
        /*Datos del cliente*/
        SELECT clientes.cliente_id, clientes.sic_tipo_tarjeta, clientes.sic_puntos, clientes.sic_dinero_electronico, clientes.sic_hereda_valorpuntos, clientes.sic_valor_puntos, tipos_clientes.sic_valor_puntos
        FROM clientes, tipos_clientes
        WHERE clientes.cliente_id = new.cliente_id and clientes.tipo_cliente_id = tipos_clientes.tipo_cliente_id
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

                    cliente_total_puntos = cliente_total_puntos - (new.dscto_importe/valor_puntos) + (old.dscto_importe/valor_puntos);
                    valor_puntos_pago =  valor_puntos;
                    puntos_pago =  new.dscto_importe/valor_puntos;
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
    '''

triggers['DOCTOS_PV_AD_PUNTOS'] = '''
	CREATE OR ALTER TRIGGER DOCTOS_PV_AD_PUNTOS FOR DOCTOS_PV
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
        doctos_pv.cliente_id = clientes.cliente_id
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

triggers['CLIENTES_BU_PUNTOS'] = '''
	CREATE OR ALTER TRIGGER CLIENTES_BU_PUNTOS FOR CLIENTES
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