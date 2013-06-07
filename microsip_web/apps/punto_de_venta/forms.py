#encoding:utf-8
from django import forms

import autocomplete_light
from microsip_web.apps.inventarios.models import *
from microsip_web.apps.ventas.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from models import *

class ArticuloManageForm(forms.ModelForm):
	
	class Meta:
		model = Articulos
		exclude= {
			'cuenta_ventas',
			'es_almacenable',
		}

class ClienteManageForm(forms.ModelForm):
	
	class Meta:
		widgets = autocomplete_light.get_widgets_dict(Cliente)
		model = Cliente
		exclude= {
			'cuenta_xcobrar',
		}

class TipoClienteManageForm(forms.ModelForm):
	class Meta:
		model = TipoCliente

class LineaArticulosManageForm(forms.ModelForm):
	class Meta:
		model = LineaArticulos
		exclude= {
			'cuenta_ventas',
		}
		
class GrupoLineasManageForm(forms.ModelForm):
	class Meta:
		model = GrupoLineas
		exclude= {
			'cuenta_ventas',
		}

class InformacionContableManageForm(forms.ModelForm):
	condicion_pago_contado 	= forms.ModelChoiceField(queryset= CondicionPago.objects.all(), required=True)

	class Meta:
		model = InformacionContable_pv

class GenerarPolizasManageForm(forms.Form):
	fecha_ini 					= forms.DateField()
	fecha_fin 					= forms.DateField()
	ignorar_documentos_cont 	= forms.BooleanField(required=False, initial=True)
	CREAR_POR = (
	    ('Dia', 'Dia'),
	    ('Periodo', 'Periodo'),
	)
	crear_polizas_por 			= forms.ChoiceField(choices=CREAR_POR)

	plantilla_ventas 			= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='V'), required=False)
	plantilla_devoluciones 		= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='D'), required=False)
	plantilla_cobros_cc 		= forms.ModelChoiceField(queryset= PlantillaPolizas_pv.objects.filter(tipo='P'), required=False)
	descripcion 				= forms.CharField(max_length=100, required=False)
	TIPOS =(
		('', '------------------'),
        ('V', 'Ventas de mostrador'),
        ('D', 'Devoluciones'),
        ('P', 'Cobros ctas. por cobrar'),
    )
	crear_polizas_de 			= forms.ChoiceField(choices=TIPOS, required=True)

class ClienteSearchForm(forms.Form):
	cliente = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'autofocus':''}),required=True)

class PlantillaPolizaManageForm(forms.ModelForm):
	class Meta:
		model = PlantillaPolizas_pv

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
    )

	#tipo 					= forms.ChoiceField(choices=TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	#valor_tipo 				= forms.ChoiceField(choices=VALOR_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	# valor_iva 				= forms.ChoiceField(choices=VALOR_IVA_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)
	# valor_contado_credito 	= forms.ChoiceField(choices=VALOR_CONTADO_CREDITO_TIPOS, widget=forms.Select(attrs={'class':'span2'}),)

	posicion  		=  forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)
	asiento_ingora 	= forms.RegexField(regex=r'^(?:\+|-)?\d+$', widget=forms.TextInput(attrs={'class':'span1'}), required= False)

	class Meta:
		widgets = autocomplete_light.get_widgets_dict(DetallePlantillaPolizas_pv)
		model = DetallePlantillaPolizas_pv

	def clean_cuenta_co(self):
	    cuenta_co = self.cleaned_data['cuenta_co']
	    if CuentaCo.objects.filter(cuenta_padre=cuenta_co.id).count() > 0:
	    	raise forms.ValidationError(u'la cuenta contable (%s) no es de ultimo nivel, por favor seleciona una cuenta de ultimo nivel' % cuenta_co )
	    return cuenta_co
	    
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