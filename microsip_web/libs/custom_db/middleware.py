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
        
        profile = UserProfile.objects.get(usuario=uid)
        
        if profile:
            return profile.basedatos_activa
        else:
            return None
    except:
        return None