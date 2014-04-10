from django import forms
from .models import *
import autocomplete_light

class SearchForm(forms.Form):
    inicio = forms.DateField(widget = forms.TextInput( attrs = { 'class' : 'input-small', 'placeholder': 'inicio...',} ), required=False)
    fin = forms.DateField(widget = forms.TextInput( attrs = { 'class' : 'input-small', 'placeholder': 'fin...', } ), required=False)
    cliente = forms.ModelChoiceField( queryset = Cliente.objects.all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required = False )