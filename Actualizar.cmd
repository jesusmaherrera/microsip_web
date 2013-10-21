echo off
color 7F
echo 			==================================
echo 			=                                =
echo 			=     ACTUALIZANDO APLICACION    =
echo 			=                                =
echo 			=   [ POR FAVOR NO CERRAR!!!!! ]  =
echo 			=                                =
echo 			==================================
echo.
echo.

git reset --hard
git pull origin master
git gc
python manage.py syncdb --no-initial-data
no




