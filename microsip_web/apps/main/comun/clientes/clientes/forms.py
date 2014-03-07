#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from .models import *
import autocomplete_light

class filtro_clientes_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    cliente = forms.ModelChoiceField(Cliente.objects.all(), widget=autocomplete_light.ChoiceWidget('ClienteAutocomplete'), required= False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Filtro por nombre...'}),required=False)
    
class ClienteManageForm(forms.ModelForm):
    
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(Cliente)
        model = Cliente

        exclude= {
            'cuenta_xcobrar',
            'estatus',
            'tipo_cliente',
        }

class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = ClienteDireccion
        exclude = (
            'cliente',
            'nombre_consignatario',
            'pais',
            'estado',
            'es_ppal',
            'poblacion',
            'referencia',
            )

