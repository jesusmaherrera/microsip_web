#encoding:utf-8
from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory, modelformset_factory

from .models import *

class CondicionPagoManageForm(forms.ModelForm):
    class Meta:
        model = CondicionPago
        exclude= (
        	'dias_ppag',
			'porcentaje_descuento_ppago',
        )

class CondicionPagoPlazoManageForm(forms.ModelForm):
    class Meta:
        model = CondicionPagoPlazo

def CondicionPagoPlazoFormset(form, formset = BaseInlineFormSet, **kwargs):
    return inlineformset_factory(CondicionPago, CondicionPagoPlazo, form, formset, **kwargs)