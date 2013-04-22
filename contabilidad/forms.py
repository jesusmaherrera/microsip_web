#encoding:utf-8
from django import forms
from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.forms import formsets
from models import *
import autocomplete_light
from django.forms.models import modelformset_factory

class InformacionContableManageForm(forms.ModelForm):
	cuenta_proveedores 	= forms.ModelChoiceField(queryset=CuentaCo.objects.all().order_by('cuenta'), required=True)
	class Meta:
		model = InformacionContable_C

class Cuenta_DIOTManageForm(forms.ModelForm):
	#cuenta = forms.ModelChoiceField(queryset=CuentaCo.objects.all().order_by('cuenta'), required=True)
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(Cuenta_DIOT)
		model = Cuenta_DIOT

Cuenta_DIOTFormset = modelformset_factory(Cuenta_DIOT, Cuenta_DIOTManageForm, can_delete=True, extra=1)