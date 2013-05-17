#encoding:utf-8
from django import forms
from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms import formsets
from models import *
import autocomplete_light
from django.forms.models import modelformset_factory

class InformacionContableManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(InformacionContable_C)
		model = InformacionContable_C

# class Cuenta_DIOTManageForm(forms.ModelForm):
# 	class Meta:
# 		widgets = autocomplete_light.get_widgets_dict(Cuenta_DIOT)
# 		model = Cuenta_DIOT

# Cuenta_DIOTFormset = modelformset_factory(Cuenta_DIOT, Cuenta_DIOTManageForm, can_delete=True, extra=1)

class GenerarDIOTManageForm(forms.Form):
	fecha_ini 				= forms.DateField()
	fecha_fin 				= forms.DateField()