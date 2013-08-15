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


cd C:\microsip_web_compilado
git clean -df & git checkout -- microsip_web\apps\
git checkout -- microsip_web\apps\
git checkout -- microsip_web\libs\
git checkout -- microsip_web\static\
git checkout -- microsip_web\templates\
git checkout -- microsip_web\urls\
git checkout -- docs\
git checkout -- requirements\
git checkout -- Actualizar.lnk
git checkout -- extras\scripts\actualizar_microsip_apps.cmd
git checkout -- search_client.url
git checkout -- Iniciar.lnk
git pull origin master
git gc
C:\Python27\python manage.py syncdb 
yes
EXPLORER.EXE http://127.0.0.1:8000/inicializar_tablas
C:\Python27\python manage.py runserver 127.0.0.1:8000


