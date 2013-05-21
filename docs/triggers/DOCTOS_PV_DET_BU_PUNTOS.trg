CREATE OR ALTER trigger doctos_pv_det_bu_puntos for doctos_pv_det
active before update position 0
AS
declare variable cliente_id integer;
declare variable tipo_tarjeta char(1);
/* PUNTOS */
declare variable puntos_articulo integer;
declare variable puntos_grupo integer;
declare variable puntos_linea integer;

declare variable puntos integer;
declare variable total_puntos integer;
/* DINERO ELECRONICO */
declare variable pct_dinero_electronico_articulo double PRECISION;
declare variable pct_dinero_electronico_linea double PRECISION;
declare variable pct_dinero_electronico_grupo double PRECISION;
declare variable pct_dinero_electronico double PRECISION;

declare variable dinero_electronico double PRECISION;
declare variable dinero_electronico_acomulado double PRECISION;

BEGIN
    /*Datos del cliente*/
    SELECT clientes.puntos_acomulados, clientes.cliente_id, clientes.tipo_tarjeta, clientes.dinero_electronico_acomulado
    FROM clientes, doctos_pv
    WHERE
        doctos_pv.docto_pv_id = new.docto_pv_id and
        doctos_pv.cliente_id = clientes.cliente_id
    INTO total_puntos, cliente_id, tipo_tarjeta, dinero_electronico_acomulado;
    
    IF (dinero_electronico_acomulado IS NULL) then
            dinero_electronico_acomulado = 0;
    /*Datos del articulo*/
    SELECT articulos.puntos, articulos.dinero_electronico, lineas_articulos.puntos, lineas_articulos.dinero_electronico,  grupos_lineas.puntos, grupos_lineas.dinero_electronico
    FROM articulos, lineas_articulos, grupos_lineas
    WHERE
        lineas_articulos.linea_articulo_id = articulos.linea_articulo_id AND
        grupos_lineas.grupo_linea_id = lineas_articulos.grupo_linea_id AND
        articulos.articulo_id = new.articulo_id
    INTO puntos_articulo, pct_dinero_electronico_articulo, puntos_linea, pct_dinero_electronico_linea, puntos_grupo, pct_dinero_electronico_grupo;
    
    if (total_puntos is null) then
        total_puntos = 0;

    total_puntos = total_puntos - old.puntos;
    dinero_electronico_acomulado = dinero_electronico_acomulado - old.dinero_electronico;

    update clientes set puntos_acomulados=:total_puntos, dinero_electronico_acomulado=:dinero_electronico_acomulado where cliente_id = :cliente_id;

    if(tipo_tarjeta = 'P') then
    begin
        IF (total_puntos IS NULL) then
            total_puntos = 0;
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

        total_puntos = total_puntos + (new.unidades * puntos);
        new.puntos = new.unidades * puntos;
/*        update doctos_pv_det set puntos=:puntos where doctos_pv_det.docto_pv_det_id = new.docto_pv_det_id;*/
        update clientes set puntos_acomulados =:total_puntos where cliente_id = :cliente_id;

    end
    else if(tipo_tarjeta = 'D') then
    begin

        IF (dinero_electronico_acomulado IS NULL) then
            dinero_electronico_acomulado = 0;

        /*Si el articulos no tiene dinero electronico busca en lineas*/
        IF ((pct_dinero_electronico_articulo IS NULL) or (pct_dinero_electronico_articulo = 0)) then
        BEGIN
            /*Si la linea no tiene puntos busca grupos */
            IF ((pct_dinero_electronico_articulo is null)or (pct_dinero_electronico_linea = 0)) then
                pct_dinero_electronico = pct_dinero_electronico_grupo;
            ELSE
                pct_dinero_electronico = pct_dinero_electronico_linea;
        END
        ELSE
            pct_dinero_electronico = pct_dinero_electronico_articulo;

        IF (pct_dinero_electronico IS NULL) then
            pct_dinero_electronico = 0;

        dinero_electronico = (new.unidades * new.precio_unitario) * (pct_dinero_electronico /100);
        dinero_electronico_acomulado = dinero_electronico_acomulado - old.dinero_electronico + dinero_electronico;

        new.dinero_electronico = dinero_electronico;
/*        update doctos_pv_det set dinero_electronico=dinero_electronico where doctos_pv_det.docto_pv_det_id = new.docto_pv_det_id;*/
        update clientes set dinero_electronico_acomulado =:dinero_electronico_acomulado where cliente_id = :cliente_id;
    end
END