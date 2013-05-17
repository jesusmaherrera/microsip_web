#encoding:utf-8
from django import forms

import autocomplete_light

from microsip_web.apps.inventarios.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
     
class DoctosInManageForm(forms.ModelForm):
	file_inventario = forms.CharField(widget=forms.FileInput, required = False)
	
	class Meta:
		model = DoctosIn
		exclude = (
			'cancelado',
			'aplicado',
			'forma_emitida',
			'contabilizado',
			'sistema_origen',
			'naturaleza_concepto',
			'usuario_creador',
			'fechahora_creacion',
			'usuario_ult_modif',
			'fechahora_ult_modif',
			)

class DoctosInDetManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DoctosInDet)
		model = DoctosInDet
		exclude = (
			'tipo_movto',
			'almacen',
			'concepto',
			'metodo_costeo',
			'rol',
			'cancelado',
			'aplicado',
			'costeo_pend',
			'pedimento_pend',
			'fecha',)

class DoctosInvfisManageForm(forms.ModelForm):
	file_inventario = forms.CharField(widget=forms.FileInput, required = False)
	
	class Meta:
		model = DoctosInvfis
		exclude = (
			'cancelado',
			'aplicado',
			'usuario_creador',
			'fechahora_creacion',
			'usuario_aut_creacion',
			'usuario_ult_modif',
			'fechahora_ult_modif',
			'usuario_aut_modif',
			)

class DoctosInvfisDetManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DoctosInvfisDet)
		model 	= DoctosInvfisDet
		exclude = (
			'claveArticulo',
			)

def doctoIn_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(DoctosIn, DoctosInDet, form, formset, **kwargs)

def inventarioFisico_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(DoctosInvfis, DoctosInvfisDet, form, formset, **kwargs)


