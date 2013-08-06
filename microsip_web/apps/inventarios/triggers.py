triggers = {}


triggers['SIC_PUERTA_INV_DOCTOSIN_BU'] = '''
    CREATE OR ALTER TRIGGER SIC_PUERTA_INV_DOCTOSIN_BU FOR DOCTOS_IN
    ACTIVE BEFORE UPDATE POSITION 0
    AS
    declare variable invfis_id integer;

    declare variable invfis_det_id integer;
    declare variable invfis_articulo_unidades integer;

    declare variable inv_articulo_id integer;
    declare variable inv_articulo_unidades integer;
    declare variable inv_detalle_id integer;

    declare variable art_discreto_id integer;
    declare variable almacen_id integer;
    declare variable inv_tipo char(1);
    declare variable seguimiento char(1);

    declare variable docto_invfis_fecha date;
    declare variable docto_in_fecha date;

    begin
        /*exception ex_saldo_cargo_excedido 'saldo';*/
        /* Este triger sirve para cuando se cancela un documento */
        if (new.cancelado='S') then
        begin
            /*Datos de documento in*/
            select first 1 doctos_in.naturaleza_concepto, doctos_in.almacen_id, doctos_in.fecha
            from doctos_in
            where doctos_in.docto_in_id = new.docto_in_id
            INTO :inv_tipo, :almacen_id, :docto_in_fecha;
        
            /*Datos de inventario fisico abierto*/
            select first 1 doctos_invfis.docto_invfis_id, doctos_invfis.fecha
            from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= :almacen_id
            INTO :invfis_id, :docto_invfis_fecha;
        
            /*Si existe un inventario fisico [abierto] del almacen del cual es este documento*/
            if (not invfis_id is null and docto_in_fecha >= docto_invfis_fecha) then
            begin
                /*Se recorren todos los detalles del documento[entrada/salida]*/
                for select articulo_id, unidades, docto_in_det_id
                from doctos_in_det
                where docto_in_id = new.docto_in_id
                into :inv_articulo_id, :inv_articulo_unidades, :inv_detalle_id
                do
                begin
                    select docto_invfis_det_id, unidades
                    from doctos_invfis_det
                    where docto_invfis_id = :invfis_id and articulo_id =:inv_articulo_id
                    into :invfis_det_id, :invfis_articulo_unidades;


                    if (not invfis_det_id is null) then
                    begin

                        if(inv_tipo='E') then
                            invfis_articulo_unidades = invfis_articulo_unidades - inv_articulo_unidades;
                        else if (inv_tipo='S') then
                        begin
                            select seguimiento from articulos where articulo_id = :inv_articulo_id
                            into :seguimiento;
                            
                            if (seguimiento <> 'S') then
                                invfis_articulo_unidades = invfis_articulo_unidades + inv_articulo_unidades;
                        end
                        if (invfis_articulo_unidades < 0 ) then
                            invfis_articulo_unidades = 0;
                        update doctos_invfis_det set unidades= :invfis_articulo_unidades where docto_invfis_det_id = :invfis_det_id;
                    end

                end
            end
        end
    end
    '''


#############################
#                           #
#   DESGLOSE EN DISCRETOS   #
#                           #
#############################

    
triggers['SIC_PUERTA_INV_DESGLOSEDIS_AI'] = '''
    CREATE OR ALTER TRIGGER SIC_PUERTA_INV_DESGLOSEDIS_AI FOR DESGLOSE_EN_DISCRETOS
    ACTIVE AFTER INSERT POSITION 0
    AS
    declare variable articulo_id integer;
    declare variable docto_invfis_det_id integer;
    declare variable almacen_id integer;
    declare variable invfis_id integer;
    declare variable desglose_discr_invfis_id integer;
    declare variable articulo_clave char(20);
    declare variable naturaleza_concepto char(1);
    declare variable cantidad_articulos integer;
    declare variable docto_invfis_fecha date;
    declare variable docto_in_fecha date;
    begin
        select doctos_in.almacen_id, doctos_in_det.articulo_id, doctos_in.naturaleza_concepto, doctos_in.fecha
        from doctos_in_det,doctos_in
        where
            doctos_in.docto_in_id = doctos_in_det.docto_in_id and
            doctos_in_det.docto_in_det_id = new.docto_in_det_id
        into :almacen_id, :articulo_id, :naturaleza_concepto, :docto_in_fecha;

        /*clave del articulo*/
        select first 1 clave_articulo from claves_articulos where articulo_id = :articulo_id into :articulo_clave;

        /*datos de inventario fisico abierto*/
        select first 1 doctos_invfis.docto_invfis_id, doctos_invfis.fecha
        from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= :almacen_id
        INTO :invfis_id, :docto_invfis_fecha;
        
        if (docto_in_fecha >= docto_invfis_fecha) then
        begin
            select docto_invfis_det_id from doctos_invfis_det where articulo_id = :articulo_id into :docto_invfis_det_id;
    
            if (not invfis_id is null) then
            begin
                /*Si es una entrada*/
                if (naturaleza_concepto = 'E') then
                begin
                    /*Si no existe el detalle de inventario fisico se crea este*/
                    if (docto_invfis_det_id is null) then
                    begin
                        docto_invfis_det_id = GEN_ID(ID_DOCTOS,1);
                        insert into doctos_invfis_det values(:docto_invfis_det_id, :invfis_id, :articulo_clave, :articulo_id, 0,null, null,null);
                    end
    
                    select first 1 desgl_discreto_invfis_id from desglose_en_discretos_invfis
                    where docto_invfis_det_id=:docto_invfis_det_id and art_discreto_id = new.art_discreto_id
                    into :desglose_discr_invfis_id;
    
                    if (desglose_discr_invfis_id is null) then
                        insert into desglose_en_discretos_invfis values(-1, :docto_invfis_det_id, new.art_discreto_id, new.unidades);
                end
                /*Si es una salida*/
                else if  (naturaleza_concepto = 'S')then
                begin
                    select first 1 desgl_discreto_invfis_id from desglose_en_discretos_invfis
                    where docto_invfis_det_id=:docto_invfis_det_id and art_discreto_id = new.art_discreto_id
                    into :desglose_discr_invfis_id;
    
                    if (not desglose_discr_invfis_id is null) then
                    begin
                        delete from desglose_en_discretos_invfis where desgl_discreto_invfis_id = :desglose_discr_invfis_id;
    
                        select unidades from doctos_invfis_det
                        where docto_invfis_det_id = :docto_invfis_det_id
                        into cantidad_articulos;
                        cantidad_articulos = cantidad_articulos - 1;
                        if (cantidad_articulos < 0 ) then
                            cantidad_articulos = 0;
        
                        update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :docto_invfis_det_id;
                    end
                end
            end
        end
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
    declare variable docto_in_tipo char(1);
    declare variable seguimiento char(1);
    declare variable docto_invfis_fecha date;
    declare variable docto_in_fecha date;

    begin
        /*Datos de documento in*/
        select first 1 doctos_in.naturaleza_concepto, doctos_in.almacen_id, doctos_in.fecha
        from doctos_in
        where doctos_in.docto_in_id = new.docto_in_id
        INTO :docto_in_tipo, :almacen_id, :docto_in_fecha;

        /*Datos de inventario fisico abierto*/
        select first 1 doctos_invfis.docto_invfis_id, doctos_invfis.fecha
        from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= :almacen_id
        INTO :invfis_id, :docto_invfis_fecha;
    
        if (not invfis_id is null and docto_in_fecha >= docto_invfis_fecha) then
        begin
            select doctos_invfis_det.docto_invfis_det_id, doctos_invfis_det.articulo_id, doctos_invfis_det.unidades
            from doctos_invfis, doctos_invfis_det
            where
                doctos_invfis.docto_invfis_id = doctos_invfis_det.docto_invfis_id and
                doctos_invfis.docto_invfis_id = :invfis_id and
                doctos_invfis_det.articulo_id = new.articulo_id
            into :invfis_det_id, :articulo_id, :cantidad_articulos;

            if (new.unidades is null) then
                new.unidades = 0;
            if (cantidad_articulos is null) then
                cantidad_articulos = 0;
                                
            if (not invfis_det_id is null) then
            begin
                if (docto_in_tipo='E') then
                    cantidad_articulos = cantidad_articulos + new.unidades;
                else if (docto_in_tipo='S') then
                begin
                    select seguimiento from articulos where articulo_id = new.articulo_id
                    into :seguimiento;
                    
                    if (seguimiento <> 'S') then
                        cantidad_articulos = cantidad_articulos - new.unidades;
                end

                if (cantidad_articulos < 0 ) then
                    cantidad_articulos = 0;

                update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;
            end
            else
            begin
                if (docto_in_tipo='E') then
                    insert into doctos_invfis_det (docto_invfis_det_id, docto_invfis_id, clave_articulo, articulo_id, unidades)
                        values(-1, :invfis_id, new.clave_articulo, new.articulo_id, new.unidades);
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
    declare variable articulo_discreto_id integer;
    declare variable docto_in_tipo char(1);
    declare variable articulo_seguimiento char(1);
    declare variable docto_invfis_fecha date;
    declare variable docto_in_fecha date;

    begin

        /*Datos de documento in*/
        select first 1 doctos_in.naturaleza_concepto, doctos_in.fecha
        from doctos_in
        where doctos_in.docto_in_id = old.docto_in_id
        INTO :docto_in_tipo, :docto_in_fecha;
    
        /*Datos de inventario fisico abierto*/
        select first 1 doctos_invfis.docto_invfis_id, doctos_invfis.fecha
        from doctos_invfis where doctos_invfis.aplicado ='N' and doctos_invfis.almacen_id= old.almacen_id
        INTO :invfis_id, :docto_invfis_fecha;

        if (not invfis_id is null and docto_in_fecha >= docto_invfis_fecha) then
        begin

            for
                select doctos_invfis_det.docto_invfis_det_id, doctos_invfis_det.articulo_id, doctos_invfis_det.unidades, articulos.seguimiento
                from doctos_invfis_det, articulos
                where
                    doctos_invfis_det.docto_invfis_id =  :invfis_id and
                    doctos_invfis_det.articulo_id = articulos.articulo_id
                into :invfis_det_id, :articulo_id, :cantidad_articulos, articulo_seguimiento
            do
            begin

                if (articulo_id = old.articulo_id and docto_in_tipo='E') then
                begin
                    cantidad_articulos = cantidad_articulos - old.unidades;

                    /*Eliminar desgloses de inventario fisico*/
                    delete from desglose_en_discretos_invfis
                    where art_discreto_id in (
                        select desglose_en_discretos.art_discreto_id from desglose_en_discretos, doctos_in_det
                        where
                        desglose_en_discretos.docto_in_det_id = doctos_in_det.docto_in_det_id and
                        doctos_in_det.docto_in_det_id = old.docto_in_det_id
                        ) and
                        docto_invfis_det_id = :invfis_det_id;
                end
                else if (articulo_id = old.articulo_id and docto_in_tipo='S') then
                begin
                    cantidad_articulos = cantidad_articulos + old.unidades;

                    for select desglose_en_discretos.art_discreto_id
                    from desglose_en_discretos, doctos_in_det
                    where
                        desglose_en_discretos.docto_in_det_id = doctos_in_det.docto_in_det_id and
                        doctos_in_det.docto_in_det_id = old.docto_in_det_id
                    into :articulo_discreto_id
                    do
                    begin
                        insert into desglose_en_discretos_invfis values(-1,:invfis_det_id, :articulo_discreto_id, 1);
                    end
                end
                if (cantidad_articulos <0 ) then
                    cantidad_articulos = 0;
                update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;

            end
        end
    end
    '''