#encoding:utf-8
from django import forms
from models import *
import autocomplete_light

class filtroarticulos_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    articulo = forms.ModelChoiceField(Articulos.objects.all(), widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'), required= False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Nombre...'}),required=False)

class filtro_clientes_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    cliente = forms.ModelChoiceField(Cliente.objects.all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required= False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Filtro por nombre...'}),required=False)

class ConexionManageForm(forms.ModelForm):
    class Meta:
        model = ConexionDB