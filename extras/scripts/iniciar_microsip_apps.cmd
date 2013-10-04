echo off
color 7F
echo 			==================================
echo 			=                                =
echo 			=     SERVIDOR DE PAGINA WEB     =
echo 			=                                =
echo 			=   [ POR FAVOR NO CERRAR!!!! ]  =
echo 			=                                =
echo 			==================================
echo.
echo.


cd /d %0\..
cd..
cd..
python manage.py runserver 0.0.0.0:8000
