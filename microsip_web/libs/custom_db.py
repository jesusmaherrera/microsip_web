trigers = {}

#####################
#                   #
#   DOCTOS_IN_DET   #
#                   #
#####################

trigers['DOCTOS_IN_DET_BI_PUERTA_ABIERTA'] = 
	'''	
	CREATE OR ALTER TRIGGER DOCTOS_IN_DET_BI_PUERTA_ABIERTA FOR DOCTOS_IN_DET
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

trigers['DOCTOS_IN_DET_BD_PUERTA_ABIERTA'] = 	
	'''
	CREATE OR ALTER TRIGGER DOCTOS_IN_DET_BD_PUERTA_ABIERTA FOR DOCTOS_IN_DET
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
	                begin
	                    cantidad_articulos = cantidad_articulos - old.unidades;
	                    update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;
	                end
	                else if (articulo_id = old.articulo_id and docto_in_tipo='S') then
	                begin
	                    cantidad_articulos = cantidad_articulos + old.unidades;
	                    update doctos_invfis_det set unidades= :cantidad_articulos where docto_invfis_det_id = :invfis_det_id;
	                end
	            end
	        end
	end
	'''

#####################
#                   #
#     DOCTOS_IN     #
#                   #
#####################

trigers['DOCTOS_IN_BU_PUERTA_ABIERTA'] =
	'''
	CREATE OR ALTER TRIGGER DOCTOS_IN_BU_PUERTA_ABIERTA FOR DOCTOS_IN
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