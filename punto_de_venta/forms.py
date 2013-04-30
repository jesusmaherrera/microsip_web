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


class DocumentoPV_ManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(Docto_PV)
		model = Docto_PV
		exclude = (
			'forma_global_emitida',
			'modalidad_facturacion',
			'total_fpgc',
			'email_envio',
			'cajero',
			'clave_cliente',
			'direccion_cliente',
			'tipo_descuento',
			'porcentaje_descuento',
			'importe_descuento',
			'persona',
			'tipo_cambio',
			'cliente_fac',
			'caja',
			'clave_cliente_fac',
			'clave_global_emitida',
			'unidad_comprom',
			'es_cfd',
			'total_impuestos',
			'estado',
			'cargar_sun',
			'impuesto_incluido',
			'importe_donativo',
			'tipo',
			'enviado',
			'unid_comprom',
			'refer_reting',
			'moneda',
			'importe_neto',
			'ticket_emitido',
			'aplicado',
			'forma_emitida',
			'contabilizado',
			'sistema_origen',
			'usuario_creador',
			'fechahora_creacion',
			'usuario_ult_modif',
			'fechahora_ult_modif',
			)

class DocumentoPVDet_ManageForm(forms.ModelForm):
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DoctosInDet)
		model = Docto_pv_det
		exclude = (
			'rol',
			'precio_modificado',
			'notas',
			'precio_unitario_impto',
			'clave_articulo',
			'porcentaje_comis',
			'es_tran_elect',
			'porcentaje_descuento',
			'fpgc_unitario',
			'vendedor',
			'posicion',
			'estatus_tran_elect',
			'precio_modificado',
			'unidades_dev',
			)

class Docto_pv_cobro_ManageForm(forms.ModelForm):
	class Meta:
		model = Docto_pv_cobro
		exclude = (
			'importe_mon_doc',
			'tipo',
			'tipo_cambio',
		)

def DocumentoPV_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(Docto_PV, Docto_pv_det, form, formset, **kwargs)

def DocumentoPV_cobro_items_formset(form, formset = BaseInlineFormSet, **kwargs):
	return inlineformset_factory(Docto_PV, Docto_pv_cobro, form, formset, **kwargs)