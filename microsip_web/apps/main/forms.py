#encoding:utf-8
from django import forms
from ...libs.api.models import *
import autocomplete_light
from django.contrib.auth.forms import AuthenticationForm

class filtroarticulos_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    articulo = forms.ModelChoiceField(Articulos.objects.all(), widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'), required= False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Nombre...'}),required=False)

class ConexionManageForm(forms.ModelForm):
    password =  forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = ConexionDB

class AplicationPluginForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'span7', 'rows':3, 'placeholder': 'Descripcion...',}))

    class Meta:
        model = AplicationPlugin