# def get_database_inuse
# 

class MainRouter(object):
    """
    A router to control all database operations on models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'config':
            return 'config'
        elif model._meta.app_label == 'auth':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'config':
            return 'config'
        elif model._meta.app_label == 'auth':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label  == obj2._meta.app_label:
           return True
        return False

    def allow_syncdb(self, db, model):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if model._meta.app_label == 'config' or db == 'config':
            return False
        elif model._meta.app_label == 'auth' and db != 'default':
            return False
        elif db == 'default' and \
            ( model._meta.app_label == 'main' or model._meta.app_label == 'cuentas_por_pagar' or  \
                model._meta.app_label == 'ventas' or model._meta.app_label == 'cuentas_por_cobrar' or model._meta.app_label == 'punto_de_venta' ):
            return False
        else:
            return True
        #     else:
        #         return False
        # elif model._meta.app_label == 'django'
        #     return True
        # elif model._meta.app_label == 'main':
        #     return True

        return None