CREATE OR ALTER trigger doctos_pv_det_ad_puntos for doctos_pv_det
active after delete position 0
AS
declare variable cliente_id integer;
/* PUNTOS */
declare variable total_puntos integer;
declare variable dinero_electronico_acomulado double PRECISION;
BEGIN
    /*Datos del cliente*/
    SELECT clientes.puntos_acomulados, clientes.cliente_id, clientes.dinero_electronico_acomulado
    FROM clientes, doctos_pv
    WHERE
        doctos_pv.docto_pv_id = old.docto_pv_id and
        doctos_pv.cliente_id = clientes.cliente_id
    INTO total_puntos, cliente_id, dinero_electronico_acomulado;
    
    IF (dinero_electronico_acomulado IS NULL) then
            dinero_electronico_acomulado = 0;

    if (total_puntos is null) then
        total_puntos = 0;

    total_puntos = total_puntos - old.puntos;
    dinero_electronico_acomulado = dinero_electronico_acomulado - old.dinero_electronico;

    update clientes set puntos_acomulados=:total_puntos, dinero_electronico_acomulado=:dinero_electronico_acomulado where cliente_id = :cliente_id;
end
