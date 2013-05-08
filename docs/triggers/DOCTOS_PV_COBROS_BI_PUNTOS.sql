AS
declare variable nombre_forma_cobro char(100);
declare variable puntos_cliente integer;
declare variable cliente_id integer;
begin
    select formas_cobro.nombre from formas_cobro where formas_cobro.forma_cobro_id = new.forma_cobro_id
    into nombre_forma_cobro;

    if (nombre_forma_cobro = 'Dinero Electronico') then
    begin
        select libres_clientes.puntos, libres_clientes.cliente_id
        from libres_clientes, doctos_pv
        where
            libres_clientes.cliente_id = doctos_pv.cliente_id and
            doctos_pv.docto_pv_id = new.docto_pv_id
        into puntos_cliente, cliente_id;
        puntos_cliente = puntos_cliente - new.importe;
        IF (puntos_cliente >= 0) then
            UPDATE libres_clientes SET puntos = :puntos_cliente WHERE cliente_id = :cliente_id;
    end
end