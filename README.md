DELETE FROM DJANGO_CONTENT_TYPE WHERE APP_LABEL='api';
error en content type

select b.articulo_id, b.entradas, c.salidas from doctos_in_det a INNER JOIN
        (select sum(doctos_in_det.unidades) as entradas, doctos_in_det.articulo_id from doctos_in_det
            where doctos_in_det.tipo_movto = 'E' group by doctos_in_det.articulo_id) b
            on a.articulo_id = b.articulo_id
            inner join
        (select sum(doctos_in_det.unidades) as salidas, doctos_in_det.articulo_id from doctos_in_det
            where doctos_in_det.tipo_movto = 'S' group by doctos_in_det.articulo_id) c
            on a.articulo_id = c.articulo_id

## Descripción
**Inventario físico a puerta abierta** es una herramienta para el apoyo a la hora de realizar un inventario físico **en Microsip** sin necesidad de cerrar la empresa.

El inventario fisico lo puede realizar con con **cualquier dispositivo que tenga un explorador web** _(smart phone,tablet, ipod, ipad, laptop, o con una terminal con lector de código de barras)_.

![pantalla de inventario fisico](https://fbcdn-sphotos-e-a.akamaihd.net/hphotos-ak-frc3/1269640_589440644431008_338792098_o.jpg)
![Inventario físico mobile](https://fbcdn-sphotos-g-a.akamaihd.net/hphotos-ak-ash3/602930_589443801097359_1377843750_n.jpg)
## Funcionamiento
### Aplicación Web

**Seleccionar artículos a inventariar**

lo puede hacer ya sea **por medio de alguna clave del articulo** o por el **nombre del articulo** 
al momento de seleccionar un articulo en el inventario si este articulo ya se a inventariado nos mostrara un mensaje de los detalles de este como que usuario, donde y que cantidad de unidades puso **[SYSDBA/Estante1=100]**:

![detalles articulo](https://scontent-a-lax.xx.fbcdn.net/hphotos-ash3/598877_589449747763431_479784911_n.jpg)

Realizar busqueda de claves de articulo.

Solo con **introducir una parte de la clave y presionar [ENTER]** se mostrara una pantalla con todas los articulos que tienen una clave parecida.

![clave_search](https://scontent-a-sjc.xx.fbcdn.net/hphotos-prn1/625534_594153823959690_463924809_n.png)

El filtro por nombre de articulo es por medio de una auto-completado el cual conforme va escribiendo el nombre del articulo, los artículos de microsip se van filtrando.

![fIltro por articulo](https://scontent-b-lax.xx.fbcdn.net/hphotos-prn2/p480x480/1375691_589451821096557_570111113_n.jpg)

### Aplicación **Microsip**

Dentro de la aplicación Microsip **cualquier** movimiento que tenga que ver con inventarios ya sean _compra, venta, traspaso de almacén, etc._ afectara a nuestro inventario físico abierto desde el momento en que se cree el inventario físico abierto hasta que este mismo se aplique.

> Si capturo **10 artículos(lápiz)** en inventario físico y posteriormente hago la venta de **5 artículos(lápiz)** en el inventario físico automáticamente se me van a rebajar esos últimos 5 artículos.

> Si posteriormente realizo una compra de 6 artículos(lápiz) como resultado en mi inventario tendré **11 artículos(lápiz)**

## Importante
Para un mejor resultado al momento de realizar un inventario físico es de vital importancia tomar en cuenta los siguientes puntos.

* En el periodo que se realice el inventario es necesario **separar las compras  y devoluciones**
* En caso de tener el mismo articulo en varios estantes (**comunicar al personal de ventas para que tome los artículos del estante donde ya se contaron** si es el caso en que ya se contaron [si no se an contado no hay problema la aplicación ignorara estos])

PLANTILLAS

//////////////////////////////// PLANTILLAS DE VENTAS, CUENTAS POR COBRAR, Y PUNTO DE VENTA /////////////////////////////////////

                                                FACTURAS      DEVOLUCIONES
Clientes                                            C               A     

Bancos                                              C               A

Descuentos                                          C               A

ventas
    -Ambos                                          A               C
    -Contado
        - Al 16                                     A               C
        - Al 0                                      A               C
        - Ambos                                     A               C
        - x...                                      A               C
    -Credito
        - Al 16                                     A               C
        - Al 0                                      A               C
        - Ambos                                     A               C
        - x...                                      A               C
IVA
    - Contado (IVA efectivo cobrado)                A               C
    - Credito (IVA pendiente cobrar)                A               C
    - Ambos                                         A               C

SEGMENTOS (etc...)                                 C-A             C-A

////////////////////////////PLANTILLAS DE CUENTAS POR PAGAR, COMPRAS ////////////////////////////////

Proveedores                                         A

Bancos                                              A

Descuentos                                          C

Compras                                             C
    -Ambos
    -Contado                                        C
        - Al 16                                     C
        - Al 0                                      C
        - Ambos                                     C
    -Credito                                        C
        - Al 16                                     C
        - Al 0                                      C
        - Ambos                                     C
IVA
    - Contado (IVA efectivo pagado)                 C
    - Credito (IVA pendiente pagar)                 C
    - Ambos                                         C    

SEGMENTOS (Fletes, etc...)                         C-A


//////PUNTO DE VENTA////////////////////
TIPOS DE POLIZAS 
ventas                      :Ingresos
devoluciones                :Diario
Cobros cuentas por cobrar   :Ingresos
