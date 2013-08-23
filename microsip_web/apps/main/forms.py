#encoding:utf-8
from django import forms
from models import *
import autocomplete_light

class filtroarticulos_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Nombre...'}),required=False)

    def __init__(self,*args,**kwargs):
        database = kwargs.pop('database')
        super(filtroarticulos_form,self).__init__(*args,**kwargs)
        self.fields['articulo'] = forms.ModelChoiceField(Articulos.objects.using(database).all(), widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete-%s'%database), required= False)
   
class filtro_clientes_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Filtro por nombre...'}),required=False)
    
    def __init__(self,*args,**kwargs):
        database = kwargs.pop('database')
        super(filtro_clientes_form,self).__init__(*args,**kwargs)
        self.fields['cliente'] = forms.ModelChoiceField(Cliente.objects.using(database).all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete-%s'%database), required= False)