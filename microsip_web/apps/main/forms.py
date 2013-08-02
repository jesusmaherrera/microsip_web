#encoding:utf-8
from django import forms
from models import *
import autocomplete_light

class filtroarticulos_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Filtro por nombre...'}),required=False)
    articulo = forms.ModelChoiceField(required= False, queryset=Articulos.objects.all().order_by('nombre'),
        widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))

class filtro_clientes_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Filtro por nombre...'}),required=False)
    cliente = forms.ModelChoiceField(required= False, queryset=Cliente.objects.all().order_by('nombre'),
        widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'))