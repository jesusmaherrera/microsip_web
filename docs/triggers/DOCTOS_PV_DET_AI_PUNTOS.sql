AS
declare variable puntos integer;
declare variable total_puntos integer;
declare variable puntos_articulo integer;
declare variable puntos_grupo integer;
declare variable puntos_linea integer;
declare variable cliente_id integer;
declare variable dinero_electronico_acomulado double PRECISION;
declare variable dinero_electronico double PRECISION;
declare variable porcentaje_dinero_electronico double PRECISION;
declare variable tipo_tarjeta char(1);
BEGIN
    /*cargamos los puntos hasta ahora de la venta y le sumamos los nuevos puntos */
    SELECT clientes.puntos_acomulados, clientes.cliente_id, clientes.tipo_tarjeta, clientes.dinero_electronico_acomulado, clientes.dinero_electronico
    FROM clientes, doctos_pv
    WHERE
        doctos_pv.docto_pv_id = new.docto_pv_id and
        doctos_pv.cliente_id = clientes.cliente_id
    INTO total_puntos, cliente_id, tipo_tarjeta, dinero_electronico_acomulado, porcentaje_dinero_electronico;

    if(tipo_tarjeta = 'P') then
    begin
        IF (total_puntos IS NULL) then
            total_puntos = 0;
    
        SELECT articulos.puntos, lineas_articulos.puntos,  grupos_lineas.puntos
        FROM articulos, lineas_articulos, grupos_lineas
        WHERE
            lineas_articulos.linea_articulo_id = articulos.linea_articulo_id AND
            grupos_lineas.grupo_linea_id = lineas_articulos.grupo_linea_id AND
            articulos.articulo_id = new.articulo_id
        INTO puntos_articulo, puntos_linea, puntos_grupo;
    
        /*Si el articulos no tiene puntos busca en lineas*/
        IF ((puntos_articulo IS NULL) or (puntos_articulo = 0) ) then
        BEGIN
            /*Si la linea no tiene puntos busca grupos */
            IF ((puntos_linea IS NULL) or (puntos_linea = 0) ) then
               puntos = puntos_grupo;
            ELSE
                puntos = puntos_linea;
        END
        ELSE
            puntos = puntos_articulo;

        total_puntos = total_puntos + puntos;
        UPDATE clientes SET puntos_acomulados =:total_puntos WHERE cliente_id = :cliente_id;

    end
    else if(tipo_tarjeta = 'D') then
    begin

        IF (dinero_electronico_acomulado IS NULL) then
            dinero_electronico_acomulado = 0;
        IF (porcentaje_dinero_electronico IS NULL) then
            porcentaje_dinero_electronico = 0;

        dinero_electronico = (new.unidades * new.precio_unitario) * (porcentaje_dinero_electronico /100);
        dinero_electronico_acomulado = dinero_electronico_acomulado + dinero_electronico;
        UPDATE clientes SET dinero_electronico_acomulado =:dinero_electronico_acomulado WHERE cliente_id = :cliente_id;
    end
END