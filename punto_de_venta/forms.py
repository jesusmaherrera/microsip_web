#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class InformacionContableManageForm(forms.ModelForm):
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

	class Meta:
		model = InformacionContable_pv

class GenerarPolizasManageForm(forms.Form):
	fecha_ini 					= forms.DateField()
	fecha_fin 					= forms.DateField()
	ignorar_documentos_cont 	= forms.BooleanField(required=False, initial=True)
	CREAR_POR = (
	    ('Documento', 'Documento'),
	    ('Dia', 'Dia'),
	    ('Periodo', 'Periodo'),
	)
	crear_polizas_por 			= forms.ChoiceField(choices=CREAR_POR)

	plantilla_ventas 			= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='V'), required=True)
	plantilla_devoluciones 		= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='D'), required=True)
	plantilla_cobros_cc 		= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo=''), required=True)
	descripcion 				= forms.CharField(max_length=100, required=False)
	TIPOS =(
        ('V', 'Ventas de mostrador'),
        ('D', 'Devoluciones'),
        ('', 'Cobros ctas. por cobrar'),
    )
	crear_polizas_de 			= forms.ChoiceField(choices=TIPOS, required=True)


class PlantillaPolizaManageForm(forms.ModelForm):
	class Meta:
		model = PlantillaPolizas_pv

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
	posicion  		=  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	asiento_ingora 	= forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_pv)
		model = DetallePlantillaPolizas_pv

def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(PlantillaPolizas_pv, DetallePlantillaPolizas_pv, form, formset, **kwargs)