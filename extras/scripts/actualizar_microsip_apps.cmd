echo off
color 30
echo 			==================================
echo 			=                                =
echo 			=     ACTUALIZANDO APLICACION    =
echo 			=                                =
echo 			=   [ POR FAVOR NO CERRAR!!!!! ]  =
echo 			=                                =
echo 			==================================
echo.
echo.


cd /d %0\..
cd..
cd..
git clean -df
git checkout
git pull origin master
git gc
C:\Python27\python manage.py syncdb 
no




