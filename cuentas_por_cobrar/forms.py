#encoding:utf-8
from django import forms

import autocomplete_light

from ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from cuentas_por_cobrar.models import *

class InformacionContableManageForm(forms.ModelForm):
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

	class Meta:
		model = InformacionContable_CC

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

	plantilla 					= forms.ModelChoiceField(queryset= PlantillaPolizas_CC.objects.all(), required=True)
	#plantilla_2 = forms.ModelChoiceField(queryset= PlantillaPolizas_V.objects.all(), required=True)
	descripcion 				= forms.CharField(max_length=100, required=False)
	crear_polizas_de 			= forms.ModelChoiceField(queryset= ConceptoCc.objects.filter(crear_polizas='S'), required=True)


class PlantillaPolizaManageForm(forms.ModelForm):
	tipo = forms.ModelChoiceField(queryset= ConceptoCc.objects.filter(crear_polizas='S'), required=True)
	class Meta:
		model = PlantillaPolizas_CC

class ConceptoPlantillaPolizaManageForm(forms.ModelForm):
	TIPOS 						= (('C', 'Cargo'),('A', 'Abono'),)
	VALOR_IVA_TIPOS             = (('A', 'Ambos'),('I', 'Solo IVA'),('0', 'Solo 0%'),)
	VALOR_CONTADO_CREDITO_TIPOS = (('Ambos', 'Ambos'),('Contado', 'Contado'),('Credito', 'Credito'),)
	VALOR_TIPOS =(
        ('Ventas', 'Ventas'),
        ('Clientes', 'Clientes'),
        ('Bancos', 'Bancos'),
        ('Descuentos', 'Descuentos'),
        ('IVA', 'IVA'),
        ('Segmento_1', 'Segmento 1'),
        ('Segmento_2', 'Segmento 2'),
        ('Segmento_3', 'Segmento 3'),
        ('Segmento_4', 'Segmento 4'),
        ('Segmento_5', 'Segmento 5'),
    )

	# tipo 					= forms.ChoiceField(choices=TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	# valor_tipo 				= forms.ChoiceField(choices=VALOR_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	# valor_iva 				= forms.ChoiceField(choices=VALOR_IVA_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	# valor_contado_credito 	= forms.ChoiceField(choices=VALOR_CONTADO_CREDITO_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)

	posicion  		=  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	asiento_ingora 	= forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)

	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_CC)
		model = DetallePlantillaPolizas_CC

def PlantillaPoliza_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(PlantillaPolizas_CC, DetallePlantillaPolizas_CC, form, formset, **kwargs)