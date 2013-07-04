import autocomplete_light
from microsip_web.apps.main.models import Articulos, DoctosInvfisDet
from django.contrib import admin

class DoctosInvfisDetAdmin(admin.ModelAdmin):
    articulo = autocomplete_light.modelform_factory(Articulos)

admin.site.register(DoctosInvfisDet, DoctosInvfisDetAdmin)
admin.site.register(Articulos)
