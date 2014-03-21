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

pip install git+https://github.com/jesusmaherrera/django-microsip-api.git
cd c:\microsip_webapps\
git update-index --assume-unchanged microsip_web/settings/local_settings.py
git pull origin master
git gc
python manage.py syncdb --noinput
echo 			=======================================
echo 			=                                     =
echo 			=       APLICACION ACTUALIZADA        =
echo 			=                                     =
echo 			=[Preciona cualquier tecla para salir]=
echo 			=                                     =
echo 			=======================================
pause




