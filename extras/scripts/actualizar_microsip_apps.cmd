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
git reset --hard
git pull origin master
git gc
python manage.py syncdb --no-initial-data
no




