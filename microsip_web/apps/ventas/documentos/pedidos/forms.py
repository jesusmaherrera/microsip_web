#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
import autocomplete_light

from models import *

class DoctoVe_ManageForm(forms.ModelForm): 
    fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'input-small'}), required= False)
    folio = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'input-small'}))
    class Meta:
        model = VentasDocumento

class DoctoVeDet_ManageForm(forms.ModelForm): 
    unidades = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'input-small'}))
    precio_unitario = forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'input-small'}))
    class Meta:
        widgets = autocomplete_light.get_widgets_dict(VentasDocumentoDetalle)
        model = VentasDocumentoDetalle

def DoctoVeDet_inlineformset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(VentasDocumento, VentasDocumentoDetalle, form, formset, **kwargs)