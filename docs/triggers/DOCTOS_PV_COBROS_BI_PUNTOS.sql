as
declare variable nombre_forma_cobro char(100);
declare variable dinero_electronico_cliente double PRECISION;
declare variable total_dinero_electronico double PRECISION;
declare variable cliente_id integer;
begin
    select formas_cobro.nombre from formas_cobro where formas_cobro.forma_cobro_id = new.forma_cobro_id
    into nombre_forma_cobro;

    if (nombre_forma_cobro = 'Dinero Electronico') then
    begin
        select clientes.dinero_electronico_acomulado, clientes.cliente_id
        from clientes, doctos_pv
        where
            doctos_pv.cliente_id = clientes.cliente_id and
            doctos_pv.docto_pv_id = new.docto_pv_id
        into dinero_electronico_cliente, cliente_id;

        total_dinero_electronico = dinero_electronico_cliente - new.importe;
        IF (total_dinero_electronico >= 0) then
            UPDATE clientes SET dinero_electronico_acomulado = :total_dinero_electronico WHERE cliente_id = :cliente_id;
        ELSE
            EXCEPTION EX_CLIENTE_SIN_SALDO 'EL CLIENTE NO TIENE SUFICIENTE DINERO ELECTRONICO, EL CLIENTE SOLO TIENE (' || dinero_electronico_cliente || ')';
    end
end