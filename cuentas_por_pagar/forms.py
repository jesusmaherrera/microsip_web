#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class ProveedorManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(Proveedor)
		model = Proveedor

class InformacionContableManageForm(forms.ModelForm):
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPagoCp.objects.all(), required=True)

	class Meta:
		model = InformacionContable_CP

class GenerarPolizasManageForm(forms.Form):
	fecha_ini 				= forms.DateField()
	fecha_fin 				= forms.DateField()
	ignorar_documentos_cont 	= forms.BooleanField(required=False, initial=True)
	CREAR_POR = (
	    ('Documento', 'Documento'),
	    ('Dia', 'Dia'),
	    ('Periodo', 'Periodo'),
	)
	crear_polizas_por 		= forms.ChoiceField(choices=CREAR_POR)

	plantilla 	= forms.ModelChoiceField(queryset= PlantillaPolizas_CP.objects.all(), required=True)
	#plantilla_2 = forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.all(), required=True)
	descripcion = forms.CharField(max_length=100, required=False)
	
	crear_polizas_de 		= forms.ModelChoiceField(queryset= ConceptoCp.objects.filter(crear_polizas='S'), required=True)


class PlantillaPolizaManageForm(forms.ModelForm):
	tipo = forms.ModelChoiceField(queryset= ConceptoCp.objects.filter(crear_polizas='S'), required=True)
	class Meta:
		model = PlantillaPolizas_CP

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
	posicion  		=  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	#cuenta_co 		= forms.ModelChoiceField(queryset=CuentaCo.objects.all().order_by('cuenta'), required=True)
	asiento_ingora 	= forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_CP)
		model = DetallePlantillaPolizas_CP

def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(PlantillaPolizas_CP, DetallePlantillaPolizas_CP, form, formset, **kwargs)