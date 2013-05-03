"""See https://docs.djangoproject.com/en/dev/topics/db/multi-db/#using-routers 
for details on db routers."""

class MicrosipRouter(object): 
    """
    inventarios/models.py => microsip, otros => default
    """
    def db_for_read(self, model, **hints):
        "Point all operations on chinook models to 'chinookdb'"
        if model._meta.app_label == 'inventarios':
            return 'microsip'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on inventarios models to 'microsip'"
        if model._meta.app_label == 'inventarios':
            return 'microsip'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a both models in inventarios app"
        if obj1._meta.app_label == 'inventarios' and obj2._meta.app_label == 'inventarios':
            return True
        # Allow if neither is chinook app
        elif 'inventarios' not in [obj1._meta.app_label, obj2._meta.app_label]: 
            return True
        return False
    
    #PROBLEMA NO SE CREA LA BASE DE DATOS EN LA TABLA NE MICROSIP SI NO EN LA OTRA
    def allow_syncdb(self, db, model):
        if db == 'microsip' or model._meta.app_label == "inventarios":
            if model._meta.db_table == 'inventarios_informacioncontable':
                return True # we're not using syncdb on our legacy database
            else:
                return False
        else: # but all other models/databases are fine
            return True