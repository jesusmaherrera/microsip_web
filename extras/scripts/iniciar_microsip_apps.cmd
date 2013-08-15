echo off
color 30
echo 			==================================
echo 			=                                =
echo 			=     SERVIDOR DE PAGINA WEB     =
echo 			=                                =
echo 			=   [ POR FAVOR NO CERRAR!!!! ]  =
echo 			=                                =
echo 			==================================
echo.
echo.


cd C:\microsip_web_compilado
C:\Python27\python manage.py runserver 127.0.0.1:8000
