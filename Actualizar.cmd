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

git update-index --assume-unchanged microsip_web/settings/local_settings.py
git pull origin master
git gc
python manage.py syncdb --no-initial-data
no




