AS

DECLARE VARIABLE PUNTOS INTEGER;
DECLARE VARIABLE TOTAL_PUNTOS INTEGER;
DECLARE VARIABLE LINEA_ARTICULO_ID INTEGER;
DECLARE VARIABLE GRUPO_LINEA_ID INTEGER;
DECLARE VARIABLE ARTICULO_ID INTEGER;

BEGIN
  FOR SELECT ARTICULO_ID
    FROM DOCTOS_PV_DET
    WHERE DOCTOS_PV_DET.docto_pv_id = NEW.docto_pv_id
    INTO ARTICULO_ID
  DO
  BEGIN
    SELECT PUNTOS
    FROM LIBRES_ARTICULOS
    WHERE LIBRES_ARTICULOS.articulo_id = :ARTICULO_ID
    INTO PUNTOS;

    IF (PUNTOS IS NULL or (0) ) then
    BEGIN
        SELECT LINEA_ARTICULO_ID
        FROM ARTICULOS
        WHERE ARTICULOS.articulo_id = :ARTICULO_ID
        INTO LINEA_ARTICULO_ID;

        SELECT PUNTOS
        FROM main_libres_linea_articulos
        WHERE main_libres_linea_articulos.linea_id = :linea_articulo_id
        INTO PUNTOS;

        IF (PUNTOS IS NULL or (0) ) then
        BEGIN
            SELECT GRUPO_LINEA_ID
            FROM LINEAS_ARTICULOS
            WHERE LINEAS_ARTICULOS.linea_articulo_id = :linea_articulo_id
            INTO GRUPO_LINEA_ID;
    
            SELECT PUNTOS
            FROM MAIN_LIBRES_GRUPO_LINEAS
            WHERE MAIN_LIBRES_GRUPO_LINEAS.grupo_id = :grupo_linea_id
            INTO PUNTOS;
        END
    END
    /*:total_puntos = :total_puntos + puntos*/
  END

END