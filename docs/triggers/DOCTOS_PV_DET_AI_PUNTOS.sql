AS
declare variable puntos integer;
declare variable total_puntos integer;
declare variable puntos_articulo integer;
declare variable puntos_grupo integer;
declare variable puntos_linea integer;
declare variable cliente_id integer;
BEGIN
    SELECT libres_articulos.puntos, lineas_articulos.puntos,  grupos_lineas.puntos
    FROM libres_articulos, articulos, lineas_articulos, grupos_lineas
    WHERE
        libres_articulos.articulo_id = articulos.articulo_id AND
        lineas_articulos.linea_articulo_id = articulos.linea_articulo_id AND
        lineas_articulos.grupo_linea_id = grupos_lineas.grupo_linea_id AND
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
    
    /*cargamos los puntos hasta ahora de la venta y le sumamos los nuevos puntos */
    SELECT libres_clientes.puntos, libres_clientes.cliente_id FROM libres_clientes, doctos_pv
    WHERE
        doctos_pv.docto_pv_id = new.docto_pv_id and
        doctos_pv.cliente_id = libres_clientes.cliente_id
    INTO total_puntos, cliente_id;

    IF (total_puntos IS NULL) then
        total_puntos = 0;
    total_puntos = total_puntos + puntos;
    UPDATE libres_clientes SET puntos =:total_puntos WHERE cliente_id = :cliente_id;
END