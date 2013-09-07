from threading import local
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from microsip_web.apps.main.models import UserProfile
my_local_global = local()

class CustomerMiddleware(object):
    def process_request(self, request):
        my_local_global.database_name, my_local_global.conexion_activa = get_database_name(request)

def get_database_name(request):
    session_key = request.session.session_key
    
    try:
        session = Session.objects.get(session_key=session_key)
    except:
        return None, None
    else:
        uid = session.get_decoded().get('_auth_user_id')
        if uid:
            user = User.objects.get(pk=uid)
            
            profile = UserProfile.objects.get(usuario=uid)
            if profile:
                try:
                    return profile.basedatos_activa, profile.conexion_activa.id
                except:
                    return None, None
            else:
                return None, None
        else:
            return None, None
