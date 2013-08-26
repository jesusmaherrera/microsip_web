from threading import local
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from microsip_web.apps.main.models import UserProfile
my_local_global = local()

class CustomerMiddleware(object):
    def process_request(self, request):
        my_local_global.database_name = get_database_name(request)

def get_database_name(request):
    session_key = request.session.session_key
    try:
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)
         
        profile = UserProfile.objects.get(pk=uid)
 
        if profile:
            return profile.conexion_activa
        else:
            return None
    except:
        return None
#     # db= fdb.connect(host="localhost",user="SYSDBA",password="masterkey",database="C:\Microsip datos\DJANGO.FDB")
#     # cur = db.cursor()
#     # cur.execute("SELECT SESSION_DATA FROM DJANGO_SESSION WHERE SESSION_KEY=%s"%session_key)
#     # empresas_rows = cur.fetchall()
#     # return 'AD2007'
#     try:
#         session = Session.objects.get(session_key=session_key)
#         uid = session.get_decoded().get('_auth_user_id')
#         user = User.objects.get(pk=uid)

#         profile = UserProfile.objects.get(pk=uid)

#         return 'AD2007'
#         # if profile:
            
#         # else:
#         #     return None
#     except:
#         return None