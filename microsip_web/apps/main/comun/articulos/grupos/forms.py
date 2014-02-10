#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from .models import *
import autocomplete_light

class GrupoLineasManageForm(forms.ModelForm):
    class Meta:
        model = GrupoLineas
        exclude= {
            'cuenta_ventas',
        }